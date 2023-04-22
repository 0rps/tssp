export interface IBidResponse {
  price: number;
  external_id: string;
  image_url: string;
  cat: string[];
  team: string;
  click: boolean;
  conversion: boolean;
  final_pctr: number;
  final_pcvr: number;
  final_price: number;
  image_size: {
    w: number;
    h: number;
  }
}
