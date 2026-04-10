/**
 * MWS Tables FUSION API Client
 * Документация: docs/FUSION-API-GUIDE.md
 */

const BASE_URL = '/api/mws' // Proxied through backend
const MWS_API_URL = 'https://tables.mws.ru/fusion/v1'

interface MWSConfig {
  apiKey?: string
  spaceId?: string
}

class MWSClient {
  private apiKey: string
  private spaceId: string

  constructor(config: MWSConfig = {}) {
    this.apiKey = config.apiKey || import.meta.env.VITE_MWS_API_KEY || ''
    this.spaceId = config.spaceId || import.meta.env.VITE_MWS_SPACE_ID || ''
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${BASE_URL}${endpoint}`

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.apiKey}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`MWS API Error: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    return data.data
  }

  // ==================== SPACES ====================

  async getSpaces() {
    return this.request<{ spaces: Space[] }>('/spaces')
  }

  // ==================== NODES ====================

  async getNodes(spaceId?: string) {
    const id = spaceId || this.spaceId
    return this.request<{ nodes: Node[] }>(`/spaces/${id}/nodes`)
  }

  async getNodeDetails(nodeId: string) {
    return this.request<Node>(`/nodes/${nodeId}`)
  }

  // ==================== DATASHEETS ====================

  async createDatasheet(data: CreateDatasheetRequest, spaceId?: string) {
    const id = spaceId || this.spaceId
    return this.request<Datasheet>(`/spaces/${id}/datasheets`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async deleteDatasheet(dstId: string, spaceId?: string) {
    const id = spaceId || this.spaceId
    return this.request(`/spaces/${id}/datasheet/${dstId}`, {
      method: 'DELETE',
    })
  }

  // ==================== RECORDS ====================

  async getRecords(dstId: string, options: GetRecordsOptions = {}) {
    const params = new URLSearchParams()

    if (options.viewId) params.append('viewId', options.viewId)
    if (options.pageSize) params.append('pageSize', options.pageSize.toString())
    if (options.pageNum) params.append('pageNum', options.pageNum.toString())
    if (options.filterByFormula) params.append('filterByFormula', options.filterByFormula)
    if (options.fieldKey) params.append('fieldKey', options.fieldKey)

    const query = params.toString() ? `?${params.toString()}` : ''
    return this.request<RecordsResponse>(`/datasheets/${dstId}/records${query}`)
  }

  async createRecords(dstId: string, records: CreateRecordInput[]) {
    return this.request<{ records: Record[] }>(`/datasheets/${dstId}/records`, {
      method: 'POST',
      body: JSON.stringify({ records, fieldKey: 'name' }),
    })
  }

  async updateRecords(dstId: string, records: UpdateRecordInput[]) {
    return this.request<{ records: Record[] }>(`/datasheets/${dstId}/records`, {
      method: 'PATCH',
      body: JSON.stringify({ records, fieldKey: 'name' }),
    })
  }

  async deleteRecords(dstId: string, recordIds: string[]) {
    const params = new URLSearchParams()
    params.append('recordIds', recordIds.join(','))
    return this.request(`/datasheets/${dstId}/records?${params.toString()}`, {
      method: 'DELETE',
    })
  }

  // ==================== FIELDS ====================

  async getFields(dstId: string, viewId?: string) {
    const query = viewId ? `?viewId=${viewId}` : ''
    return this.request<{ fields: Field[] }>(`/datasheets/${dstId}/fields${query}`)
  }

  async createField(dstId: string, field: CreateFieldInput, spaceId?: string) {
    const id = spaceId || this.spaceId
    return this.request<Field>(`/spaces/${id}/datasheets/${dstId}/fields`, {
      method: 'POST',
      body: JSON.stringify(field),
    })
  }

  // ==================== VIEWS ====================

  async getViews(dstId: string) {
    return this.request<{ views: View[] }>(`/datasheets/${dstId}/views`)
  }

  async createView(dstId: string, view: CreateViewInput, spaceId?: string) {
    const id = spaceId || this.spaceId
    return this.request<View>(`/spaces/${id}/datasheets/${dstId}/views`, {
      method: 'POST',
      body: JSON.stringify(view),
    })
  }

  // ==================== ATTACHMENTS ====================

  async uploadAttachment(dstId: string, file: File, recordId?: string, fieldId?: string) {
    const formData = new FormData()
    formData.append('file', file)

    const params = new URLSearchParams()
    if (recordId) params.append('recordId', recordId)
    if (fieldId) params.append('fieldId', fieldId)
    const query = params.toString() ? `?${params.toString()}` : ''

    const response = await fetch(`${BASE_URL}/datasheets/${dstId}/attachments${query}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`)
    }

    const data = await response.json()
    return data.data as Attachment
  }

  getAttachmentUrl(dstId: string, token: string) {
    return `${BASE_URL}/datasheets/${dstId}/attachments?token=${encodeURIComponent(token)}`
  }
}

// ==================== TYPES ====================

export interface Space {
  id: string
  name: string
  isAdmin?: boolean
}

export interface Node {
  id: string
  name: string
  type: 'Folder' | 'Datasheet'
  icon?: string
  isFav?: boolean
  permission?: number
  children?: Node[]
}

export interface Datasheet {
  id: string
  createdAt: number
  fields: { id: string; name: string }[]
}

export interface Record {
  recordId: string
  fields: { [key: string]: any }
  createdAt?: number
  updatedAt?: number
}

export interface Field {
  id: string
  name: string
  type: FieldType
  desc?: string
  property?: any
}

export type FieldType =
  | 'SingleText'
  | 'Text'
  | 'SingleSelect'
  | 'MultiSelect'
  | 'Number'
  | 'Currency'
  | 'Percent'
  | 'DateTime'
  | 'Attachment'
  | 'Member'
  | 'Checkbox'
  | 'Rating'
  | 'URL'
  | 'Phone'
  | 'Email'
  | 'OneWayLink'
  | 'TwoWayLink'
  | 'MagicLookUp'
  | 'Formula'
  | 'AutoNumber'
  | 'CreatedTime'
  | 'LastModifiedTime'
  | 'CreatedBy'
  | 'LastModifiedBy'

export interface View {
  id: string
  name: string
  type: string
}

export interface Attachment {
  token: string
  name: string
  size: number
  mimeType: string
  url?: string
}

export interface CreateDatasheetRequest {
  name: string
  description?: string
  folderId?: string
  fields?: CreateFieldInput[]
}

export interface CreateFieldInput {
  type: FieldType
  name: string
  property?: any
}

export interface GetRecordsOptions {
  viewId?: string
  pageSize?: number
  pageNum?: number
  filterByFormula?: string
  fieldKey?: 'name' | 'id'
}

export interface RecordsResponse {
  total: number
  pageNum: number
  pageSize: number
  records: Record[]
}

export interface CreateRecordInput {
  fields: { [key: string]: any }
}

export interface UpdateRecordInput {
  recordId: string
  fields: { [key: string]: any }
}

export interface CreateViewInput {
  name: string
  properties: {
    type: 'Grid' | 'Kanban' | 'Gantt' | 'Calendar' | 'Gallery' | 'Architecture'
    settings?: any
  }
}

// Export singleton instance
export const mwsClient = new MWSClient()

export default MWSClient
