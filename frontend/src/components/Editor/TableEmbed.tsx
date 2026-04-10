import { useState, useEffect } from 'react'
import { ExternalLink, RefreshCw, Settings, X } from 'lucide-react'
import { mwsClient, Record, Field } from '../../api/mwsClient'

interface TableEmbedProps {
  datasheetId: string
  viewId?: string
  onRemove?: () => void
}

export function TableEmbed({ datasheetId, viewId, onRemove }: TableEmbedProps) {
  const [records, setRecords] = useState<Record[]>([])
  const [fields, setFields] = useState<Field[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tableName, setTableName] = useState('')

  useEffect(() => {
    loadTableData()
  }, [datasheetId, viewId])

  const loadTableData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load fields and records in parallel
      const [fieldsData, recordsData] = await Promise.all([
        mwsClient.getFields(datasheetId, viewId),
        mwsClient.getRecords(datasheetId, { viewId, pageSize: 50 }),
      ])

      setFields(fieldsData.fields)
      setRecords(recordsData.records)

      // Get table name from node details
      try {
        const nodeDetails = await mwsClient.getNodeDetails(datasheetId)
        setTableName(nodeDetails.name)
      } catch {
        setTableName(datasheetId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки таблицы')
    } finally {
      setLoading(false)
    }
  }

  const getCellValue = (record: Record, field: Field): string => {
    const value = record.fields[field.name]
    if (value === null || value === undefined) return ''
    if (Array.isArray(value)) return value.join(', ')
    if (typeof value === 'object') return JSON.stringify(value)
    return String(value)
  }

  if (loading) {
    return (
      <div className="my-4 p-6 border border-mws-gray-200 rounded-xl bg-mws-gray-50 animate-pulse">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-5 h-5 bg-mws-gray-200 rounded" />
          <div className="w-32 h-4 bg-mws-gray-200 rounded" />
        </div>
        <div className="space-y-2">
          <div className="w-full h-8 bg-mws-gray-200 rounded" />
          <div className="w-full h-8 bg-mws-gray-200 rounded" />
          <div className="w-full h-8 bg-mws-gray-200 rounded" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="my-4 p-4 border border-red-200 rounded-xl bg-red-50 text-red-700">
        <div className="flex items-center justify-between">
          <span className="text-sm">{error}</span>
          <button onClick={loadTableData} className="p-1 hover:bg-red-100 rounded">
            <RefreshCw size={14} />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="my-4 border border-mws-gray-200 rounded-xl overflow-hidden group">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-mws-gray-50 border-b border-mws-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-lg">📊</span>
          <span className="font-medium text-sm text-mws-gray-700">{tableName}</span>
          <span className="text-xs text-mws-gray-400">
            {records.length} записей
          </span>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={loadTableData}
            className="p-1.5 hover:bg-mws-gray-200 rounded"
            title="Обновить"
          >
            <RefreshCw size={14} className="text-mws-gray-500" />
          </button>
          <a
            href={`https://tables.mws.ru/workbench/${datasheetId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 hover:bg-mws-gray-200 rounded"
            title="Открыть в MWS Tables"
          >
            <ExternalLink size={14} className="text-mws-gray-500" />
          </a>
          {onRemove && (
            <button
              onClick={onRemove}
              className="p-1.5 hover:bg-red-100 rounded"
              title="Удалить"
            >
              <X size={14} className="text-red-500" />
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="bg-mws-gray-50 sticky top-0">
            <tr>
              {fields.slice(0, 8).map((field) => (
                <th
                  key={field.id}
                  className="px-4 py-2 text-left font-medium text-mws-gray-600 border-b border-mws-gray-200 whitespace-nowrap"
                >
                  {field.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.recordId} className="hover:bg-mws-gray-50">
                {fields.slice(0, 8).map((field) => (
                  <td
                    key={`${record.recordId}-${field.id}`}
                    className="px-4 py-2 border-b border-mws-gray-100 text-mws-gray-700 max-w-[200px] truncate"
                  >
                    {getCellValue(record, field)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      {records.length === 50 && (
        <div className="px-4 py-2 bg-mws-gray-50 border-t border-mws-gray-200 text-xs text-mws-gray-400 text-center">
          Показаны первые 50 записей
        </div>
      )}
    </div>
  )
}

// Table picker modal for slash command
interface TablePickerProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (datasheetId: string) => void
}

export function TablePicker({ isOpen, onClose, onSelect }: TablePickerProps) {
  const [tables, setTables] = useState<{ id: string; name: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadTables()
    }
  }, [isOpen])

  const loadTables = async () => {
    try {
      setLoading(true)
      const nodes = await mwsClient.getNodes()
      const datasheets = flattenNodes(nodes.nodes).filter(
        (n) => n.type === 'Datasheet'
      )
      setTables(datasheets.map((d) => ({ id: d.id, name: d.name })))
    } catch (err) {
      console.error('Failed to load tables:', err)
    } finally {
      setLoading(false)
    }
  }

  const flattenNodes = (nodes: any[]): any[] => {
    return nodes.reduce((acc, node) => {
      acc.push(node)
      if (node.children) {
        acc.push(...flattenNodes(node.children))
      }
      return acc
    }, [])
  }

  const filteredTables = tables.filter((t) =>
    t.name.toLowerCase().includes(search.toLowerCase())
  )

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-[480px] max-h-[70vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-mws-gray-200">
          <h2 className="font-semibold text-mws-gray-700">Вставить таблицу</h2>
          <button onClick={onClose} className="p-1 hover:bg-mws-gray-100 rounded">
            <X size={16} className="text-mws-gray-500" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-mws-gray-200">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск таблицы..."
            className="w-full px-3 py-2 border border-mws-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        {/* Table list */}
        <div className="flex-1 overflow-y-auto p-2">
          {loading ? (
            <div className="p-4 text-center text-mws-gray-400">Загрузка...</div>
          ) : filteredTables.length === 0 ? (
            <div className="p-4 text-center text-mws-gray-400">
              Таблицы не найдены
            </div>
          ) : (
            filteredTables.map((table) => (
              <button
                key={table.id}
                onClick={() => {
                  onSelect(table.id)
                  onClose()
                }}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-mws-gray-50 text-left"
              >
                <span className="text-lg">📊</span>
                <div>
                  <div className="font-medium text-sm text-mws-gray-700">
                    {table.name}
                  </div>
                  <div className="text-xs text-mws-gray-400">{table.id}</div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
