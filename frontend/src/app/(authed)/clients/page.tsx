"use client";

import {
  Table,
  Title,
  Group,
  Button,
  Modal,
  Stack,
  TextInput,
} from "@mantine/core";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useApi } from "@/api/context";
import { Client } from "@/types/clients";

import styles from "./page.module.scss";

export default function ClientsPage() {
  const api = useApi();
  const router = useRouter();

  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  // Create client modal state
  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);

  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  useEffect(() => {
    api.clients
      .listClients()
      .then(setClients)
      .finally(() => setLoading(false));
  }, [api]);

  async function handleCreateClient() {
    if (!email.trim() || !firstName.trim() || !lastName.trim()) return;

    try {
      setCreating(true);

      const newClient = await api.clients.createClient({
        email: email.trim(),
        first_name: firstName.trim(),
        last_name: lastName.trim(),
      });

      // Add to top of list immediately
      setClients((prev) => [newClient, ...prev]);

      // Reset form
      setEmail("");
      setFirstName("");
      setLastName("");
      setCreateOpen(false);
    } catch (err) {
      console.error("Failed to create client", err);
    } finally {
      setCreating(false);
    }
  }

  if (loading) {
    return <div className={styles.container}>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <Group justify="space-between" className={styles.title}>
        <Title order={2}>Clients</Title>
        <Button onClick={() => setCreateOpen(true)}>New Client</Button>
      </Group>

      {/* Create Client Modal */}
      <Modal
        opened={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Create New Client"
      >
        <Stack>
          <TextInput
            label="First Name"
            value={firstName}
            onChange={(e) => setFirstName(e.currentTarget.value)}
            required
          />

          <TextInput
            label="Last Name"
            value={lastName}
            onChange={(e) => setLastName(e.currentTarget.value)}
            required
          />

          <TextInput
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.currentTarget.value)}
            required
          />

          <Button
            onClick={handleCreateClient}
            loading={creating}
            disabled={!email.trim() || !firstName.trim() || !lastName.trim()}
          >
            Create Client
          </Button>
        </Stack>
      </Modal>

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
