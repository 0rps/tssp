export interface IBidRequest {
  id: string;
  imp: {
    banner: {
      w: number;
      h: number;
    }
  },
  click: {
    prob: number;
  },
  conv: {
    prob: number;
  },
  site: {
    domain: string;
  },
  ssp: {
    id: string;
  },
  user: {
    id: string;
  },
  bcat: string[];
}
