export interface Visit {
  id: number
  id_visitors: number
  id_type_of_proce: number
  company_represents: string
  purpose: string
  buildings_visited: string
  uadm_visited: string
  check_in: string
  check_out: string | null
  user_created: string
  names: string
  surnames: string
  id_card_number: string
  uadms_names?: string
  buildings_names?: string
}

export interface Visitor {
  id: number
  names: string
  surnames: string
  gender: string
  id_card_number: string
  id_num_control: string
  province: string
  nationality: string
  photo: string
  user_created: string
}

export interface VisitStats {
  total_visits: number
  active_visits: number
  today_visits: number
  unique_visitors: number
}
