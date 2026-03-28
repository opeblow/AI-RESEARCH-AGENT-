import api from './client'
import { QueryRequest, QueryResponse } from '../types'

export const sendQuery = async (question: string): Promise<QueryResponse> => {
  const request: QueryRequest = { question }
  const response = await api.post<QueryResponse>('/query', request)
  return response.data
}

export const checkHealth = async () => {
  const response = await api.get('/health')
  return response.data
}
