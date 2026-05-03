<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from 'vue'
import api from '@/lib/api'

interface Option {
  value: string | number
  label: string
}

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: null
  },
  options: {
    type: Array as () => Option[],
    default: () => []
  },
  placeholder: {
    type: String,
    default: 'Seleccione...'
  },
  searchable: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  apiEndpoint: {
    type: String,
    default: ''
  },
  searchParam: {
    type: String,
    default: 'search'
  },
  limit: {
    type: Number,
    default: 50
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'load'])

const isOpen = ref(false)
const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const localOptions = ref<Option[]>([])
const isLoading = ref(false)
const searchTimeout = ref<number | null>(null)

// Sync localOptions with props.options
watch(() => props.options, (newOptions) => {
  localOptions.value = [...newOptions]
}, { immediate: true, deep: true })

function getFilteredOptions(): Option[] {
  if (!searchQuery.value) return localOptions.value
  const query = searchQuery.value.toLowerCase()
  return localOptions.value.filter((opt: Option) => {
    return opt.label.toLowerCase().includes(query)
  })
}

const filteredOptions = computed(() => {
  // If modelValue is set but not in localOptions, add it as a temporary option
  const modelVal = props.modelValue
  if (modelVal && !localOptions.value.find((opt: Option) => opt.value === modelVal)) {
    return [...localOptions.value, { value: modelVal, label: String(modelVal) }]
  }
  return localOptions.value
})

const selectedLabel = computed(() => {
  const modelVal = String(props.modelValue || '').toLowerCase()
  const found = localOptions.value.find((opt: Option) => 
    String(opt.value || '').toLowerCase() === modelVal ||
    String(opt.label || '').toLowerCase() === modelVal
  )
  return found ? found.label : (props.modelValue ? String(props.modelValue) : props.placeholder)
})

async function loadOptions(search?: string) {
  if (!props.apiEndpoint) return
  
  isLoading.value = true
  try {
    const params: Record<string, unknown> = { limit: props.limit }
    if (search) params[props.searchParam] = search
    
    const response = await api.get(props.apiEndpoint, { params })
    const items = response.data.items || response.data
    
    localOptions.value = items.map((item: any) => ({
      value: item.description || item.name || item.id,
      label: item.description || item.name || item.label || String(item.id)
    }))
  } catch (error) {
    console.error('Error loading options:', error)
  } finally {
    isLoading.value = false
  }
}

function openDropdown() {
  if (props.disabled) return
  isOpen.value = true
  
  // Load options from API if endpoint is provided
  if (props.apiEndpoint) {
    loadOptions()
  }
  
  searchQuery.value = ''
  setTimeout(() => {
    searchInputRef.value?.focus()
  }, 10)
}

function closeDropdown() {
  isOpen.value = false
  searchQuery.value = ''
}

function toggleDropdown() {
  if (props.disabled) return
  
  if (isOpen.value) {
    closeDropdown()
  } else {
    openDropdown()
  }
}

function selectOption(option: Option) {
  emit('update:modelValue', option.value)
  closeDropdown()
}

function onSearchInput() {
  // Debounce search for API calls
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = setTimeout(() => {
    emit('search', searchQuery.value)
    
    if (props.apiEndpoint) {
      loadOptions(searchQuery.value)
    }
  }, 300) as unknown as number
}

function onContainerClick(event: MouseEvent) {
  event.stopPropagation()
}

onUnmounted(() => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
})
</script>

<template>
  <div ref="containerRef" class="relative" @click="onContainerClick">
    <!-- Select Trigger -->
    <div
      @click.stop="toggleDropdown"
      :class="[
        'min-h-[2.75rem] w-full rounded-lg border px-4 py-2.5 text-sm cursor-pointer flex items-center justify-between transition-colors',
        props.disabled 
          ? 'bg-gray-100 dark:bg-gray-800 cursor-not-allowed opacity-60' 
          : 'bg-white dark:bg-transparent hover:border-brand-300',
        isOpen 
          ? 'border-brand-500 ring-2 ring-brand-500/20' 
          : 'border-gray-300 dark:border-gray-700',
        !selectedLabel || selectedLabel === props.placeholder ? 'text-gray-400' : 'text-gray-800 dark:text-gray-100'
      ]"
    >
      <span class="truncate">{{ selectedLabel }}</span>
      
      <!-- Loading spinner -->
      <div v-if="isLoading" class="ml-2 flex-shrink-0">
        <span class="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></span>
      </div>
      
      <!-- Dropdown arrow -->
      <svg
        v-else
        class="ml-2 h-4 w-4 flex-shrink-0 text-gray-400 transition-transform"
        :class="{ 'rotate-180': isOpen }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>

    <!-- Dropdown Menu -->
    <div
      v-if="isOpen && !props.disabled"
      class="absolute z-50 w-full mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-auto"
      @click.stop
    >
      <!-- Search Input -->
      <div v-if="props.searchable" class="p-2 border-b border-gray-100 dark:border-gray-800">
        <input
          ref="searchInputRef"
          v-model="searchQuery"
          @input="onSearchInput"
          type="text"
          placeholder="Buscar..."
          class="w-full h-9 px-3 rounded-md border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm text-gray-800 dark:text-gray-100 placeholder:text-gray-400 focus:outline-none focus:border-brand-400"
        />
      </div>

      <!-- Options List -->
      <div class="py-1">
        <div
          v-if="filteredOptions.length === 0 && !isLoading"
          class="px-4 py-3 text-sm text-gray-400 dark:text-gray-500 text-center"
        >
          No hay resultados
        </div>
        
        <div
          v-if="isLoading"
          class="px-4 py-3 text-sm text-gray-400 dark:text-gray-500 text-center"
        >
          Cargando...
        </div>
        
        <div
          v-for="option in filteredOptions"
          :key="option.value"
          @click.stop="selectOption(option)"
          class="px-4 py-2.5 text-sm cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between"
          :class="{
            'bg-brand-50 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400 font-medium': option.value === props.modelValue
          }"
        >
          <span>{{ option.label }}</span>
          <svg
            v-if="option.value === props.modelValue"
            class="w-4 h-4 text-brand-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>