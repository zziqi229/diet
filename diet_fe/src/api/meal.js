import request from './request'

export const mealApi = {
  create: (data) => request.post('/meal/', data),
  list: (params) => request.get('/meal/', { params }),
}
