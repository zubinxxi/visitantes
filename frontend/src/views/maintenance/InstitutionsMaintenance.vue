<script setup lang="ts">
import { onMounted } from 'vue'
import { useCrud, type CrudColumn } from '@/composables/useCrud'
import CrudTable from '@/components/CrudTable.vue'

const columns: CrudColumn[] = [
  { key: 'line_num', label: '#', type: 'text' },
  { key: 'id', label: 'ID', type: 'hidden' },
  { key: 'description', label: 'Descripción', type: 'text' },
  { key: 'code_mef', label: 'Código MEF', type: 'number' },
]

const {
  items, loading, showForm, form, editingItem,
  showDeleteConfirm, deletingItem,
  page, limit, total, totalPages, limitOptions,
  loadItems, openCreate, openEdit, closeForm, saveItem,
  openDelete, closeDelete, confirmDelete,
  setSearch, changePage, changeLimit, exportToXlsx, printTable,
} = useCrud('/maintenance/institutions', columns, 'Instituciones')

onMounted(loadItems)
</script>

<template>
  <CrudTable
    :columns="columns"
    :items="items"
    :loading="loading"
    :show-form="showForm"
    :form="form"
    :editing-item="editingItem"
    :show-delete-confirm="showDeleteConfirm"
    :deleting-item="deletingItem"
    title="Instituciones"
    app-name="maint_institutions"
    :page="page"
    :limit="limit"
    :total="total"
    :total-pages="totalPages"
    :limit-options="limitOptions"
    @load="loadItems"
    @create="openCreate"
    @edit="openEdit"
    @delete="openDelete"
    @close-form="closeForm"
    @save="saveItem"
    @close-delete="closeDelete"
    @confirm-delete="confirmDelete"
    @update:form="(key, value) => form[key] = value"
    @search="setSearch"
    @change-page="changePage"
    @change-limit="changeLimit"
    @export="exportToXlsx"
    @print="printTable"
  />
</template>
