const cloud = require('wx-server-sdk')
const TcbRouter = require('tcb-router')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()
const _ = db.command
const $ = db.command.aggregate

// Collections
const RESERVATIONS = 'reservations'
const CAMPUSES = 'campuses'
const UNAVAILABLE_TIMES = 'unavailable_times'
const KEY_MANAGERS = 'key_managers'
const EQUIPMENT = 'equipment'
const EQUIPMENT_BORROWS = 'equipment_borrows'
const USERS = 'users' // Optional, for admin check if needed, or storing user profiles

exports.main = async (event, context) => {
  const app = new TcbRouter({ event })
  const wxContext = cloud.getWXContext()
  const openid = wxContext.OPENID

  app.use(async (ctx, next) => {
    try {
      await next()
    } catch (e) {
      console.error(e)
      ctx.body = { error: e.message }
    }
  })

  // --- Helpers ---
  
  // Helper to get user info (mocking the original user object)
  // In a real scenario without auth, we might trust the input or use openid
  const getUser = async (userId) => {
    // For now, we just return a mock or fetch from users collection if exists
    // If we strictly follow "remove auth", we might just use the openid as identity
    return { id: userId || openid, is_admin: true } // Defaulting to admin for "no auth" requirement? Or just permissive.
  }

  // --- User Routes ---

  app.router('user/login', async (ctx, next) => {
    if (!openid) {
      ctx.body = { user: null, error: 'OPENID not found' }
      return
    }
    const res = await db.collection(USERS).where({
      _openid: openid
    }).get()
    
    if (res.data.length > 0) {
      ctx.body = { user: res.data[0] }
    } else {
      ctx.body = { user: null }
    }
  })

  app.router('user/register', async (ctx, next) => {
    const { student_id, name, phone } = event
    
    if (!student_id || !name) {
      ctx.body = { error: 'Missing required fields' }
      return
    }
    
    // Check if already registered
    const check = await db.collection(USERS).where({
      _openid: openid
    }).get()
    
    if (check.data.length > 0) {
      ctx.body = { error: 'User already registered', user: check.data[0] }
      return
    }
    
    const res = await db.collection(USERS).add({
      data: {
        _openid: openid,
        student_id,
        name,
        phone,
        is_admin: false, // Default to false
        created_at: db.serverDate()
      }
    })
    
    ctx.body = { message: 'Registered', id: res._id }
  })

  // --- Reservation Routes ---

  app.router('reservation/campuses', async (ctx, next) => {
    const res = await db.collection(CAMPUSES).get()
    ctx.body = res.data
  })

  app.router('reservation/create', async (ctx, next) => {
    const { campus_id, date, start_hour, end_hour, student_id, name, contact } = event
    
    if (!campus_id || !date || !start_hour || !end_hour) {
      ctx.body = { error: 'Missing required fields' }
      return
    }

    // Date validation and logic
    const reservationDate = new Date(date)
    const now = new Date()
    
    // Check unavailable times
    const dayOfWeek = (reservationDate.getDay() + 6) % 7 + 1 // 1-7 (Mon-Sun) ? Original python: 0=Sun, 1=Mon... wait.
    // Python: date.weekday() is 0=Mon, 6=Sun. 
    // Original code: day_of_week = (date.weekday() + 1) % 7 -> 0=Sun, 1=Mon... 6=Sat.
    // JS: getDay() is 0=Sun, 1=Mon... 6=Sat. So JS getDay() matches the target format directly.
    const jsDayOfWeek = reservationDate.getDay()

    const unavailable = await db.collection(UNAVAILABLE_TIMES).where(_.or([
      {
        campus_id: parseInt(campus_id),
        date: date
      },
      {
        campus_id: parseInt(campus_id),
        day_of_week: jsDayOfWeek
      },
      {
        campus_id: parseInt(campus_id),
        date: null,
        day_of_week: null
      }
    ])).get()

    // Filter time overlap in memory or complex query
    // Simple overlap check: (StartA < EndB) and (EndA > StartB)
    let isUnavailable = false
    let reason = ''
    
    for (const u of unavailable.data) {
      if (u.start_hour < end_hour && u.end_hour > start_hour) {
        isUnavailable = true
        reason = u.reason || 'Time slot unavailable'
        break
      }
    }

    if (isUnavailable) {
      ctx.body = { error: reason }
      return
    }

    // Check existing reservations
    const conflict = await db.collection(RESERVATIONS).where({
      campus_id: parseInt(campus_id),
      date: date,
      status: 'active',
      start_hour: _.lt(end_hour),
      end_hour: _.gt(start_hour)
    }).count()

    if (conflict.total > 0) {
      ctx.body = { error: 'Time slot already reserved' }
      return
    }

    // Check weekly limit (6 hours)
    const d = new Date(date)
    const day = d.getDay() // 0-6
    const diff = d.getDate() - day + (day == 0 ? -6 : 1) // adjust when day is sunday
    const monday = new Date(d)
    monday.setDate(diff)
    const sunday = new Date(d)
    sunday.setDate(diff + 6)
    
    const mondayStr = monday.toISOString().split('T')[0]
    const sundayStr = sunday.toISOString().split('T')[0]

    const weeklyRes = await db.collection(RESERVATIONS).where({
        user_id: openid,
        status: 'active',
        date: _.gte(mondayStr).and(_.lte(sundayStr))
    }).get()

    let totalHours = 0
    for (const r of weeklyRes.data) {
        totalHours += (r.end_hour - r.start_hour)
    }
    
    const newHours = end_hour - start_hour
    if (totalHours + newHours > 6) {
        ctx.body = { error: `Weekly limit exceeded. Used: ${totalHours}, New: ${newHours}, Limit: 6` }
        return
    }

    // Create reservation
    const res = await db.collection(RESERVATIONS).add({
      data: {
        user_id: openid, // Use openid as user_id
        student_id: student_id || 'anonymous',
        user_name: name || 'Anonymous',
        contact: contact || '',
        campus_id: parseInt(campus_id),
        date: date,
        start_hour,
        end_hour,
        status: 'active',
        key_picked_up: false,
        key_returned: false,
        created_at: db.serverDate()
      }
    })

    ctx.body = { message: 'Reservation created', id: res._id }
  })

  app.router('reservation/my-reservations', async (ctx, next) => {
    const res = await db.collection(RESERVATIONS).where({
      user_id: openid,
      status: 'active'
    }).orderBy('date', 'desc').orderBy('start_hour', 'desc').get()
    
    ctx.body = res.data
  })

  app.router('reservation/weekly', async (ctx, next) => {
    const { campus_id } = event
    if (!campus_id) {
      ctx.body = { error: 'campus_id required' }
      return
    }

    // Calculate week range (simplified for now, client can pass range or we calculate)
    // For simplicity, just return all active future reservations or let client filter
    // But to match API, let's try to filter by date range if possible, or just return recent/future
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0]

    const res = await db.collection(RESERVATIONS).where({
      campus_id: parseInt(campus_id),
      status: 'active',
      date: _.gte(dateStr) // Simple filter for now
    }).orderBy('date', 'asc').orderBy('start_hour', 'asc').get()

    ctx.body = { reservations: res.data }
  })

  app.router('reservation/date', async (ctx, next) => {
    const { campus_id, date } = event
    if (!campus_id || !date) {
      ctx.body = { error: 'Missing parameters' }
      return
    }

    const res = await db.collection(RESERVATIONS).where({
      campus_id: parseInt(campus_id),
      date: date,
      status: 'active'
    }).orderBy('start_hour', 'asc').get()

    ctx.body = res.data
  })

  app.router('reservation/cancel', async (ctx, next) => {
    const { reservation_id } = event
    // Check ownership
    const res = await db.collection(RESERVATIONS).doc(reservation_id).get()
    if (!res.data) {
      ctx.body = { error: 'Not found' }
      return
    }
    
    if (res.data.user_id !== openid) {
       // Allow if admin (skip check for now as requested "remove auth", but ownership is logic)
       // If we strictly remove auth, maybe anyone can cancel? Let's stick to ownership or admin.
       // For "remove auth", I'll assume anyone can cancel if they have the ID, OR stick to openid.
       // Let's stick to openid for safety, unless "remove auth" means "no login required but we track users".
       // I'll allow it if it matches openid.
       if (res.data.user_id !== openid) {
           // Check if "admin" (hardcoded or from DB)
           // For now, just return error
           ctx.body = { error: 'Unauthorized' }
           return
       }
    }

    await db.collection(RESERVATIONS).doc(reservation_id).update({
      data: { status: 'cancelled' }
    })
    ctx.body = { message: 'Cancelled' }
  })

  // --- Admin Routes ---
  // "Remove auth" -> No check for admin_required decorator.

  app.router('admin/unavailable-times', async (ctx, next) => {
    if (event.httpMethod === 'POST') { // Create
        const { campus_id, start_hour, end_hour, reason, date, day_of_week } = event
        await db.collection(UNAVAILABLE_TIMES).add({
            data: {
                campus_id: parseInt(campus_id),
                start_hour,
                end_hour,
                reason,
                date,
                day_of_week,
                created_at: db.serverDate()
            }
        })
        ctx.body = { message: 'Created' }
    } else if (event.httpMethod === 'DELETE') { // Delete
        const { id } = event
        await db.collection(UNAVAILABLE_TIMES).doc(id).remove()
        ctx.body = { message: 'Deleted' }
    } else { // Get
        const { campus_id } = event
        let query = db.collection(UNAVAILABLE_TIMES)
        if (campus_id) {
            query = query.where({ campus_id: parseInt(campus_id) })
        }
        const res = await query.get()
        ctx.body = res.data
    }
  })

  app.router('admin/key-managers', async (ctx, next) => {
      if (event.httpMethod === 'POST') {
          const { campus_id, name, contact } = event
          await db.collection(KEY_MANAGERS).add({
              data: {
                  campus_id: parseInt(campus_id),
                  name,
                  contact,
                  is_active: true,
                  created_at: db.serverDate()
              }
          })
          ctx.body = { message: 'Created' }
      } else if (event.httpMethod === 'DELETE') {
          const { id } = event
          await db.collection(KEY_MANAGERS).doc(id).remove()
          ctx.body = { message: 'Deleted' }
      } else {
          const { campus_id } = event
          let query = db.collection(KEY_MANAGERS).where({ is_active: true })
          if (campus_id) {
              query = query.where({ campus_id: parseInt(campus_id) })
          }
          const res = await query.get()
          ctx.body = res.data
      }
  })

  app.router('admin/reservations', async (ctx, next) => {
      // List all reservations
      const { page = 1, page_size = 20, campus_id, start_date } = event
      let query = db.collection(RESERVATIONS)
      if (campus_id) query = query.where({ campus_id: parseInt(campus_id) })
      if (start_date) query = query.where({ date: _.gte(start_date) })
      
      const countResult = await query.count()
      const res = await query.skip((page - 1) * page_size).limit(page_size).orderBy('created_at', 'desc').get()
      
      ctx.body = {
          data: res.data,
          total: countResult.total,
          page,
          page_size
      }
  })

  // --- Key Routes ---

  app.router('key/pickup', async (ctx, next) => {
      const { reservation_id } = event
      await db.collection(RESERVATIONS).doc(reservation_id).update({
          data: {
              key_picked_up: true,
              key_pickup_time: db.serverDate()
          }
      })
      ctx.body = { message: 'Key picked up' }
  })

  app.router('key/return', async (ctx, next) => {
      const { reservation_id } = event
      await db.collection(RESERVATIONS).doc(reservation_id).update({
          data: {
              key_returned: true,
              key_return_time: db.serverDate()
          }
      })
      ctx.body = { message: 'Key returned' }
  })

  app.router('key/pickups', async (ctx, next) => {
      const { campus_id } = event
      const res = await db.collection(RESERVATIONS).where({
          campus_id: parseInt(campus_id),
          key_picked_up: true,
          status: 'active'
      }).orderBy('key_pickup_time', 'desc').limit(50).get()
      ctx.body = res.data
  })

  // --- Equipment Routes ---

  app.router('equipment/borrow', async (ctx, next) => {
      const { equipment_name, equipment_type, notes } = event
      await db.collection(EQUIPMENT_BORROWS).add({
          data: {
              user_id: openid,
              equipment_name,
              equipment_type,
              notes,
              borrow_time: db.serverDate(),
              status: 'borrowed'
          }
      })
      ctx.body = { message: 'Borrowed' }
  })

  app.router('equipment/return', async (ctx, next) => {
      const { borrow_id } = event
      await db.collection(EQUIPMENT_BORROWS).doc(borrow_id).update({
          data: {
              status: 'returned',
              return_time: db.serverDate()
          }
      })
      ctx.body = { message: 'Returned' }
  })

  app.router('equipment/list', async (ctx, next) => {
      const { campus_id, is_shared, equipment_type } = event
      let query = db.collection(EQUIPMENT)
      if (campus_id) query = query.where({ campus_id: parseInt(campus_id) })
      if (is_shared !== undefined) query = query.where({ is_shared: is_shared === 'true' || is_shared === true })
      if (equipment_type) query = query.where({ equipment_type })
      
      const res = await query.orderBy('placed_at', 'desc').get()
      ctx.body = res.data
  })

  app.router('equipment/register', async (ctx, next) => {
      const { campus_id, equipment_type, equipment_name, location, is_shared, contact, notes } = event
      await db.collection(EQUIPMENT).add({
          data: {
              user_id: openid,
              campus_id: parseInt(campus_id),
              equipment_type,
              equipment_name,
              location,
              is_shared: is_shared || false,
              contact,
              notes,
              placed_at: db.serverDate(),
              created_at: db.serverDate()
          }
      })
      ctx.body = { message: 'Registered' }
  })

  return app.serve()
}
