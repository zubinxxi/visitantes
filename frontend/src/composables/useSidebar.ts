import { ref } from 'vue'

export function useSidebar() {
  const isCollapsed = ref(false)
  const isMobileOpen = ref(false)
  const isHovered = ref(false)

  function toggleCollapse() {
    isCollapsed.value = !isCollapsed.value
  }

  function setHovered(value: boolean) {
    if (isCollapsed.value) {
      isHovered.value = value
    }
  }

  function toggleMobile() {
    isMobileOpen.value = !isMobileOpen.value
    if (!isMobileOpen.value) {
      isHovered.value = false
    }
  }

  const sidebarExpanded = () => !isCollapsed.value || isHovered.value

  return {
    isCollapsed,
    isMobileOpen,
    isHovered,
    toggleCollapse,
    toggleMobile,
    setHovered,
    sidebarExpanded,
  }
}
