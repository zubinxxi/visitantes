<script setup lang="ts" generic="T extends Record<string, unknown>">
import { ref } from 'vue'
import type { CrudColumn } from '@/composables/useCrud'
import Multiselect from 'vue-multiselect'
import { usePermissionsStore } from '@/stores/permissions'

interface Props {
  columns: CrudColumn[]
  items: Record<string, unknown>[]
  loading: boolean
  showForm: boolean
  form: Record<string, unknown>
  editingItem: Record<string, unknown> | null
  showDeleteConfirm: boolean
  deletingItem: Record<string, unknown> | null
  title: string
  newButtonText?: string
  appName?: string
  page?: number
  limit?: number
  total?: number
  totalPages?: number
  limitOptions?: { value: number; label: string }[]
}

interface Emits {
  (e: 'load'): void
  (e: 'create'): void
  (e: 'edit', item: Record<string, unknown>): void
  (e: 'delete', item: Record<string, unknown>): void
  (e: 'closeForm'): void
  (e: 'save'): void
  (e: 'closeDelete'): void
  (e: 'confirmDelete'): void
  (e: 'update:form', key: string, value: unknown): void
  (e: 'changePage', page: number): void
  (e: 'changeLimit', limit: number): void
  (e: 'search', value: string): void
  (e: 'export'): void
  (e: 'print'): void
}

const props = withDefaults(defineProps<Props>(), {
  newButtonText: 'Nuevo',
  appName: '',
  page: 1,
  limit: 10,
  total: 0,
  totalPages: 0,
  limitOptions: () => [
    { value: 10, label: '10' },
    { value: 20, label: '20' },
    { value: 30, label: '30' },
    { value: 50, label: '50' },
    { value: 100, label: '100' },
  ] as { value: number; label: string }[],
})

const permsStore = usePermissionsStore()

function canCreate(): boolean {
  return !props.appName || permsStore.canCreate(props.appName)
}
function canEditItem(): boolean {
  return !props.appName || permsStore.canEdit(props.appName)
}
function canDeleteItem(): boolean {
  return !props.appName || permsStore.canDelete(props.appName)
}
function canExportData(): boolean {
  return !props.appName || permsStore.canExport(props.appName)
}
function canPrintData(): boolean {
  return !props.appName || permsStore.canPrint(props.appName)
}

const emit = defineEmits<Emits>()

const searchValue = ref('')

const visibleColumns = props.columns.filter((c) => c.type !== 'hidden')
const formColumns = props.columns.filter((c) => c.type !== 'hidden' && c.key !== 'line_num')

function updateForm(key: string, value: unknown) {
  emit('update:form', key, value)
}

function getFieldOptions(col: CrudColumn) {
  if (col.options) return col.options
  const selectKeys = ['active', 'status', 'priv_access', 'priv_insert', 'priv_delete', 'priv_update', 'priv_export', 'priv_print', 'mfa']
  if (selectKeys.includes(col.key)) {
    return [
      { label: 'Sí', value: 'Y' },
      { label: 'No', value: 'N' },
    ]
  }
  return []
}

function isSelectField(col: CrudColumn): boolean {
  const selectKeys = ['active', 'status', 'priv_access', 'priv_insert', 'priv_delete', 'priv_update', 'priv_export', 'priv_print', 'mfa']
  return col.type === 'select' || selectKeys.includes(col.key)
}

function goToPage(newPage: number) {
  if (newPage >= 1 && newPage <= props.totalPages) {
    emit('changePage', newPage)
  }
}

function onLimitChange(value: number) {
  emit('changeLimit', value)
}

function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchValue.value = value
  emit('search', value)
}

function onSearchClear() {
  searchValue.value = ''
  emit('search', '')
}
</script>

<template>
  <div class="no-print">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-lg font-medium text-gray-800 dark:text-white">{{ title }}</h1>
        <p class="text-theme-sm text-gray-500 dark:text-gray-400">{{ total }} registros</p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <div class="relative">
          <input
            type="text"
            v-model="searchValue"
            @input="onSearchInput"
            placeholder="Buscar..."
            class="h-10 w-full sm:w-64 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 pl-10 pr-10 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <button
            v-if="searchValue"
            @click="onSearchClear"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <button
          @click="$emit('load')"
          :disabled="loading"
          class="h-10 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750 disabled:opacity-50"
          title="Refrescar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        <button
          v-if="canExportData()"
          @click="$emit('export')"
          :disabled="loading || items.length === 0"
          class="h-10 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750 disabled:opacity-50"
          title="Exportar a Excel"
        >
          <svg class="w-4 h-4 text-success-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </button>

        <button
          v-if="canPrintData()"
          @click="$emit('print')"
          :disabled="loading || items.length === 0"
          class="h-10 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750 disabled:opacity-50"
          title="Imprimir"
        >
          <svg class="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
        </button>

        <button
          v-if="canCreate()"
          @click="$emit('create')"
          class="h-10 rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
        >
          {{ newButtonText }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <span class="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
    </div>

    <div
      v-else-if="items.length === 0"
      class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs py-16 text-center"
    >
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
        <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <h3 class="mt-4 text-base font-medium text-gray-900 dark:text-white">Sin registros</h3>
      <p class="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">No hay datos disponibles</p>
    </div>

    <div v-else class="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <th v-for="col in visibleColumns" :key="col.key" :class="['px-6 py-3.5 text-left text-theme-xs font-medium uppercase text-gray-400', col.width || '']">
                {{ col.label }}
              </th>
              <th v-if="canEditItem() || canDeleteItem()" class="px-6 py-3.5 text-right text-theme-xs font-medium uppercase text-gray-400 w-20">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="(item, idx) in items" :key="String(item.id ?? item.login ?? idx)" class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td v-for="col in visibleColumns" :key="col.key" class="px-6 py-4 text-theme-sm text-gray-700 dark:text-gray-300">
                <span v-if="col.type === 'boolean'" :class="item[col.key] ? 'text-success-600 dark:text-success-400' : 'text-error-600 dark:text-error-400'">
                  <svg v-if="item[col.key]" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </span>
                <span v-else-if="col.type === 'select' && col.options && col.key === 'active'" :class="item[col.key] === 'Y' ? 'text-success-600 dark:text-success-400' : 'text-gray-400 dark:text-gray-500'">
                  <svg v-if="item[col.key] === 'Y'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                  </svg>
                </span>
                <span v-else-if="col.type === 'select' && col.options && col.key === 'priv_admin'" :class="item[col.key] === 'Y' ? 'text-success-600 dark:text-success-400' : 'text-gray-400 dark:text-gray-500'">
                  <svg v-if="item[col.key] === 'Y'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                  </svg>
                </span>
                <span v-else-if="col.type === 'color'" class="flex items-center gap-2">
                  <span
                    class="w-5 h-5 rounded-full border border-gray-300 dark:border-gray-600"
                    :style="{ backgroundColor: (item[col.key] as string) || '#ccc' }"
                  ></span>
                  <span>{{ item[col.key] || '—' }}</span>
                </span>
                <span v-else>{{ item[col.key] ?? '—' }}</span>
              </td>
              <td v-if="canEditItem() || canDeleteItem()" class="px-6 py-4 text-right">
                <div class="inline-flex gap-1 justify-end">
                  <button
                    v-if="canEditItem()"
                    @click="$emit('edit', item)"
                    class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                    title="Editar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    v-if="canDeleteItem()"
                    @click="$emit('delete', item)"
                    class="rounded-lg p-2 text-error-500 hover:bg-error-50 dark:hover:bg-error-900/20 hover:text-error-600 dark:hover:text-error-400 transition-colors"
                    title="Eliminar"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1H6a1 1 0 00-1 1v7M8 4V3" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-gray-100 dark:border-gray-800 px-6 py-4">
        <div class="flex items-center gap-2 text-theme-sm text-gray-500 dark:text-gray-400">
          <span>Mostrar</span>
          <Multiselect
            :model-value="limitOptions.find(o => o.value === limit)"
            @update:model-value="(val: any) => onLimitChange(val?.value ?? val)"
            :options="limitOptions"
            :searchable="false"
            :close-on-select="true"
            :show-labels="false"
            label="label"
            track-by="value"
            class="multiselect-dark w-24"
          />
          <span>registros por página</span>
        </div>

        <div class="flex items-center gap-1">
          <button
            @click="goToPage(page - 1)"
            :disabled="page <= 1"
            class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <template v-for="p in totalPages" :key="p">
            <button
              v-if="p === 1 || p === totalPages || (p >= page - 1 && p <= page + 1)"
              @click="goToPage(p)"
              :class="['rounded-lg px-3 py-1.5 text-theme-sm', p === page ? 'bg-brand-500 text-white' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700']"
            >
              {{ p }}
            </button>
            <span v-else-if="p === page - 2 || p === page + 2" class="px-1 text-gray-400">...</span>
          </template>

          <button
            @click="goToPage(page + 1)"
            :disabled="page >= totalPages"
            class="rounded-lg p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Form Modal -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm p-4" @click.self="$emit('closeForm')">
      <div class="w-full max-w-lg mx-auto overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-800 px-6 py-4">
          <h3 class="text-base font-medium text-gray-800 dark:text-white">
            {{ editingItem ? 'Editar registro' : 'Nuevo registro' }}
          </h3>
          <button @click="$emit('closeForm')" class="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 max-h-96 overflow-y-auto">
          <div class="space-y-4">
            <div v-for="col in formColumns" :key="col.key">
              <label class="mb-1.5 block text-theme-sm font-medium text-gray-700 dark:text-gray-300">
                {{ col.label }}<span v-if="col.required" class="text-error-500">*</span>
              </label>
              <Multiselect
                v-if="isSelectField(col)"
                :model-value="form[col.key]"
                @update:model-value="updateForm(col.key, $event)"
                :options="getFieldOptions(col)"
                :searchable="false"
                :close-on-select="true"
                placeholder="Seleccione..."
                label="label"
                track-by="value"
                class="multiselect-dark"
              />
              <input
                v-else
                :type="col.type === 'number' ? 'number' : 'text'"
                :value="form[col.key] ?? ''"
                @input="updateForm(col.key, ($event.target as HTMLInputElement).value)"
                class="h-11 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-transparent px-4 py-2.5 text-theme-sm text-gray-800 dark:text-gray-100 shadow-theme-xs placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-brand-300 focus:outline-none focus:ring-3 focus:ring-brand-500/10"
                :placeholder="col.label"
              />
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-3 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button
            @click="$emit('closeForm')"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            Cancelar
          </button>
          <button
            @click="$emit('save')"
            class="rounded-lg bg-brand-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm p-4" @click.self="$emit('closeDelete')">
      <div class="w-full max-w-md mx-auto overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-theme-xl">
        <div class="p-6 text-center">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-error-50 dark:bg-error-900/20 mb-4">
            <svg class="w-7 h-7 text-error-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-base font-medium text-gray-900 dark:text-white mb-2">Confirmar eliminación</h3>
          <p class="text-theme-sm text-gray-500 dark:text-gray-400">
            ¿Está seguro que desea eliminar este registro? Esta acción no se puede deshacer.
          </p>
        </div>
        <div class="flex justify-center gap-3 border-t border-gray-200 dark:border-gray-800 px-6 py-4">
          <button
            @click="$emit('closeDelete')"
            class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2.5 text-theme-sm font-medium text-gray-700 dark:text-gray-200 shadow-theme-xs hover:bg-gray-50 dark:hover:bg-gray-750"
          >
            Cancelar
          </button>
          <button
            @click="$emit('confirmDelete')"
            class="rounded-lg bg-error-500 px-4 py-2.5 text-theme-sm font-medium text-white shadow-theme-xs hover:bg-error-600"
          >
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
}
</style>