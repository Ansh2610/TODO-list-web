const request = require('supertest')
const mongoose = require('mongoose')
require('dotenv').config()

const { app } = require('../server/app')

beforeAll(async () => {
  process.env.NODE_ENV = 'test'
  process.env.SKIP_AUTH = 'true'
  await mongoose.connect(process.env.MONGODB_URI)
})

afterAll(async () => {
  await mongoose.connection.close()
})

describe('Todos API', () => {
  it('creates a todo', async () => {
    const res = await request(app)
      .post('/api/todos')
      .send({ text: 'Test item' })
    expect(res.statusCode).toBe(201)
    expect(res.body.success).toBe(true)
    expect(res.body.todo.text).toBe('Test item')
  })

  it('lists todos', async () => {
    const res = await request(app).get('/api/todos')
    expect(res.statusCode).toBe(200)
    expect(res.body.success).toBe(true)
    expect(Array.isArray(res.body.todos)).toBe(true)
  })
})
