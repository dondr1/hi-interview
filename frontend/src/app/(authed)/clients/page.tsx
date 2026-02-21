"use client";

import { Table, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation"; //new import for navigation

import { useApi } from "@/api/context";
import { Client } from "@/types/clients";

import styles from "./page.module.scss";

export default function ClientsPage() {
  const api = useApi();
  const router = useRouter();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.clients
      .listClients()
      .then(setClients)
      .finally(() => setLoading(false));
  }, [api]);

  if (loading) {
    return <div className={styles.container}>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <Title order={2} className={styles.title}>
        Clients
      </Title>

      <Table striped highlightOnHover withTableBorder withColumnBorders>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Name</Table.Th>
            <Table.Th>Email</Table.Th>
            <Table.Th>Assigned</Table.Th>
          </Table.Tr>
        </Table.Thead>

        <Table.Tbody>
          {clients.map((client) => (
            <Table.Tr
              key={client.id}
              className={styles.clickableRow}
              onClick={() => router.push(`/clients/${client.id}`)}
            >
              <Table.Td>
                {client.first_name} {client.last_name}
              </Table.Td>
              <Table.Td>{client.email}</Table.Td>
              <Table.Td>{client.assigned_user_id ? "Yes" : "No"}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </div>
  );
}
