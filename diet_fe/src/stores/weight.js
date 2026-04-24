import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getWeights, createWeight, updateWeight, deleteWeight } from '@/api/weight'

export const useWeightStore = defineStore('weight', () => {
  const records = ref([])
  const loading = ref(false)

  async function fetchRecords(params = {}) {
    loading.value = true
    try {
      const res = await getWeights(params)
      records.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  async function addRecord(data) {
    const res = await createWeight(data)
    return res
  }

  async function editRecord(id, data) {
    const res = await updateWeight(id, data)
    return res
  }

  async function removeRecord(id) {
    const res = await deleteWeight(id)
    return res
  }

  return { records, loading, fetchRecords, addRecord, editRecord, removeRecord }
})
