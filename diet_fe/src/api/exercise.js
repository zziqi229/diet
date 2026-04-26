import request from './request'

export const exerciseApi = {
  create: (data) => request.post('/exercise/', data),
  list: (params) => request.get('/exercise/', { params }),
}
