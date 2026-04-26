import request from './request'

export const mealApi = {
  create: (data) => request.post('/meal/', data),
  update: (id, data) => request.put(`/meal/${id}`, data),
  list: (params) => request.get('/meal/', { params }),
}
