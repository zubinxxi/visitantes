import { ref } from 'vue'
import QRCode from 'qrcode'
import type { Visit } from '@/types/visit'

export function useBadgePrinter() {
  const isPrinting = ref(false)
  const selectedVisits = ref<Visit[]>([])

  async function generateQRCode(data: string): Promise<string> {
    try {
      return await QRCode.toDataURL(data, {
        width: 128,
        margin: 1,
        color: {
          dark: '#1a2231',
          light: '#ffffff',
        },
      })
    } catch {
      return ''
    }
  }

  function toggleSelectVisit(visit: Visit) {
    const index = selectedVisits.value.findIndex((v) => v.id === visit.id)
    if (index > -1) {
      selectedVisits.value.splice(index, 1)
    } else {
      selectedVisits.value.push(visit)
    }
  }

  function isVisitSelected(visit: Visit): boolean {
    return selectedVisits.value.some((v) => v.id === visit.id)
  }

  function clearSelection() {
    selectedVisits.value = []
  }

  function printSingle(visit: Visit) {
    selectedVisits.value = [visit]
    executePrint()
  }

  function printSelected() {
    if (selectedVisits.value.length === 0) return
    executePrint()
  }

  function executePrint() {
    isPrinting.value = true
    window.print()
    setTimeout(() => {
      isPrinting.value = false
    }, 1000)
  }

  return {
    isPrinting,
    selectedVisits,
    generateQRCode,
    toggleSelectVisit,
    isVisitSelected,
    clearSelection,
    printSingle,
    printSelected,
  }
}
