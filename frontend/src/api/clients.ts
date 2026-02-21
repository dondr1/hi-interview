import { AxiosInstance } from "axios";

import { Client } from "@/types/clients";

export default class ClientsApi {
  private axiosInstance: AxiosInstance;

  constructor(axiosInstance: AxiosInstance) {
    this.axiosInstance = axiosInstance;
  }

  public listClients = async (): Promise<Client[]> => {
    const response = await this.axiosInstance.get<{ data: Client[] }>("client");
    return response.data.data;
  };

  //new: for getClient
  public getClient = async (id: string): Promise<Client> => {
    const response = await this.axiosInstance.get<Client>(`client/${id}`);
    return response.data;
  };
}
