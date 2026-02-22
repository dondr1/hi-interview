import { AxiosInstance } from "axios";

import { Client, ClientNote } from "@/types/clients";

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

  //new: for client notes
  public listClientNotes = async (clientId: string): Promise<ClientNote[]> => {
    const response = await this.axiosInstance.get<{ data: ClientNote[] }>(
      `client/${clientId}/notes`,
    );
    return response.data.data;
  };

  public createClientNote = async (
    clientId: string,
    content: string,
  ): Promise<ClientNote> => {
    const response = await this.axiosInstance.post<ClientNote>(
      `client/${clientId}/notes`,
      { content },
    );
    return response.data;
  };
}
