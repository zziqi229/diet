import request from './request'

export const getWeights = (params) => request.get('/api/weight/', { params })
export const createWeight = (data) => request.post('/api/weight/', data)
export const updateWeight = (id, data) => request.put(`/api/weight/${id}`, data)
export const deleteWeight = (id) => request.delete(`/api/weight/${id}`)
