import { ref, computed } from 'vue'
import api from '@/lib/api'
import * as XLSX from 'xlsx'
import { useToast } from './useToast'

export interface CrudItem {
  id?: number | string
  [key: string]: unknown
}

export interface CrudColumn {
  key: string
  label: string
  type?: 'text' | 'number' | 'boolean' | 'select' | 'hidden' | 'color'
  options?: { label: string; value: string | number }[]
  required?: boolean
  width?: string
}

export interface PaginatedResponse {
  items: CrudItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export function useCrud(baseUrl: string, columns: CrudColumn[], title: string = 'Datos') {
  const toast = useToast()
  const items = ref<CrudItem[]>([])
  const loading = ref(false)
  const showForm = ref(false)
  const editingItem = ref<CrudItem | null>(null)
  const showDeleteConfirm = ref(false)
  const deletingItem = ref<CrudItem | null>(null)
  const error = ref('')

  const page = ref(1)
  const limit = ref(10)
  const search = ref('')
  const total = ref(0)
  const totalPages = ref(0)

  const limitOptions = [
    { value: 10, label: '10' },
    { value: 20, label: '20' },
    { value: 30, label: '30' },
    { value: 50, label: '50' },
    { value: 100, label: '100' },
  ]

  const searchTimeout = ref<number | null>(null)

  const itemsWithLineNum = computed(() => {
    const start = (page.value - 1) * limit.value
    return items.value.map((item, index) => {
      const newItem: CrudItem = {}
      Object.keys(item).forEach((key: string) => {
        if (key !== 'line_num') {
          newItem[key] = item[key]
        }
      })
      newItem.line_num = start + index + 1
      return newItem
    })
  })

  const emptyForm = computed(() => {
    const form: Record<string, unknown> = {}
    columns.forEach((col) => {
      if (col.type === 'boolean') {
        form[col.key] = false
      } else if (col.type === 'number') {
        form[col.key] = null
      } else {
        form[col.key] = ''
      }
    })
    return form
  })

  const form = ref<Record<string, unknown>>({})

  async function loadItems(newPage?: number, newLimit?: number, newSearch?: string) {
    loading.value = true
    error.value = ''
    try {
      const params = new URLSearchParams()
      params.set('page', String(newPage ?? page.value))
      params.set('limit', String(newLimit ?? limit.value))
      if (newSearch !== undefined) {
        params.set('search', newSearch)
      } else if (search.value) {
        params.set('search', search.value)
      }

      const response = await api.get(`${baseUrl}/?${params.toString()}`)
      const data = response.data

      items.value = data.items
      total.value = data.total
      page.value = data.page
      limit.value = data.limit
      totalPages.value = data.total_pages
    } catch {
      error.value = 'Error al cargar los datos'
      toast.error('Error al cargar los datos')
    } finally {
      loading.value = false
    }
  }

  function changePage(newPage: number) {
    if (newPage >= 1 && newPage <= totalPages.value) {
      loadItems(newPage)
    }
  }

  function changeLimit(newLimit: number | { value: number }) {
    const limit = typeof newLimit === 'object' ? newLimit.value : newLimit
    loadItems(1, limit)
  }

  function setSearch(value: string) {
    search.value = value
    if (searchTimeout.value) {
      clearTimeout(searchTimeout.value)
    }
    searchTimeout.value = setTimeout(() => {
      loadItems(1, limit.value, value)
    }, 300) as unknown as number
  }

  function openCreate() {
    editingItem.value = null
    form.value = { ...emptyForm.value }
    showForm.value = true
  }

  function openEdit(item: CrudItem) {
    editingItem.value = item
    form.value = { ...emptyForm.value }
    columns.forEach((col) => {
      form.value[col.key] = item[col.key] ?? (col.type === 'boolean' ? false : '')
    })
    showForm.value = true
  }

  function closeForm() {
    showForm.value = false
    editingItem.value = null
    form.value = {}
  }

  async function saveItem() {
    error.value = ''
    try {
      const payload: Record<string, unknown> = {}
      columns.forEach((col) => {
        if (col.type !== 'hidden') {
          payload[col.key] = form.value[col.key]
        }
      })

      if (editingItem.value) {
        await api.put(`${baseUrl}/${editingItem.value.id}`, payload)
        toast.success('Registro actualizado correctamente')
      } else {
        await api.post(baseUrl, payload)
        toast.success('Registro creado correctamente')
      }

      closeForm()
      await loadItems()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Error al guardar'
      toast.error(error.value)
    }
  }

  function openDelete(item: CrudItem) {
    deletingItem.value = item
    showDeleteConfirm.value = true
  }

  function closeDelete() {
    showDeleteConfirm.value = false
    deletingItem.value = null
  }

  async function confirmDelete() {
    if (!deletingItem.value) return
    error.value = ''
    try {
      await api.delete(`${baseUrl}/${deletingItem.value.id}`)
      toast.success('Registro eliminado correctamente')
      closeDelete()
      await loadItems()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Error al eliminar'
      toast.error(error.value)
    }
  }

  function exportToXlsx() {
    const visibleColumns = columns.filter((c) => c.type !== 'hidden')
    const start = (page.value - 1) * limit.value
    const exportData = items.value.map((item, index) => {
      const row: Record<string, unknown> = { '#': start + index + 1 }
      visibleColumns.forEach((col) => {
        if (col.key !== 'id' && col.key !== 'line_num') {
          let val = item[col.key]
          if (col.type === 'boolean') {
            val = val ? 'Sí' : 'No'
          }
          row[col.label] = val ?? ''
        }
      })
      return row
    })

    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Datos')
    
    const fileName = `export_${baseUrl.replace('/', '_')}_${new Date().toISOString().split('T')[0]}.xlsx`
    XLSX.writeFile(wb, fileName)
  }

  async function printTable() {
    const visibleColumns = columns.filter((c) => c.type !== 'hidden')
    let allItems = items.value as CrudItem[]
    const startNum = 1
    
    if (!search.value) {
      try {
        const response = await api.get(`${baseUrl}/?page=1&limit=1000`)
        const data = response.data
        allItems = data.items
      } catch {
        toast.error('Error al cargar datos para imprimir')
        return
      }
    }
    
    if (allItems.length === 0) {
      toast.error('No hay datos para imprimir')
      return
    }
    
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${title} - Impresión</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; }
          h1 { font-size: 18px; margin-bottom: 10px; color: #333; }
          table { width: 100%; border-collapse: collapse; margin-top: 10px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 12px; }
          th { background: #f5f5f5; font-weight: bold; }
          tr:nth-child(even) { background: #fafafa; }
          .print-date { font-size: 10px; color: #666; margin-bottom: 10px; }
          .total-records { font-size: 11px; color: #666; margin-bottom: 10px; }
        </style>
      </head>
      <body>
        <div class="print-date">Fecha de impresión: ${new Date().toLocaleString()}</div>
        <h1>${title}</h1>
        <div class="total-records">Total de registros: ${allItems.length}</div>
        <table>
          <thead>
            <tr><th>#</th>${visibleColumns.map(col => `<th>${col.label}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${allItems.map((item, index) => `
              <tr><td>${startNum + index}</td>${visibleColumns.map(col => `<td>${item[col.key] ?? ''}</td>`).join('')}</tr>
            `).join('')}
          </tbody>
        </table>
      </body>
      </html>
    `
    
    const printWindow = window.open('', '_blank', 'width=800,height=600')
    if (printWindow) {
      printWindow.document.write(html)
      printWindow.document.close()
      setTimeout(() => {
        printWindow.print()
      }, 500)
    } else {
      toast.error('Por favor permita ventanas emergentes para imprimir')
    }
  }

  return {
    items: itemsWithLineNum,
    loading,
    error,
    columns,
    form,
    showForm,
    editingItem,
    showDeleteConfirm,
    deletingItem,
    page,
    limit,
    search,
    total,
    totalPages,
    limitOptions,
    loadItems,
    changePage,
    changeLimit,
    setSearch,
    openCreate,
    openEdit,
    closeForm,
    saveItem,
    openDelete,
    closeDelete,
    confirmDelete,
    exportToXlsx,
    printTable,
  }
}
