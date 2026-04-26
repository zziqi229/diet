import request from './request'

export const weightApi = {
  create: (data) => request.post('/weight/', data),
  list: (params) => request.get('/weight/', { params }),
}
