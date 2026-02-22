"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Badge, Button, Card, Group, Stack, Text, Title } from "@mantine/core";

import { useApi } from "@/api/context";
import { Client } from "@/types/clients";

import ClientNotesSection from "./ClientNotesSection";

export default function ClientDetailPage() {
  const params = useParams();
  const id = params?.id as string | undefined;

  const router = useRouter();
  const api = useApi();

  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    setLoading(true);

    api.clients
      .getClient(id)
      .then(setClient)
      .catch((err) => {
        console.error("Failed to fetch client", err);
        setClient(null);
      })
      .finally(() => setLoading(false));
  }, [api, id]);

  if (!id) return null;

  if (loading) return <div>Loading...</div>;

  if (!client) return <div>Client not found</div>;

  return (
    <Stack p="xl" gap="lg">
      <Button variant="subtle" onClick={() => router.push("/clients")}>
        ← Back to Clients
      </Button>

      <Group justify="space-between">
        <Title order={2}>
          {client.first_name} {client.last_name}
        </Title>
        <Badge
          variant="light"
          color={client.assigned_user_id ? "green" : "gray"}
        >
          {client.assigned_user_id ? "Assigned" : "Unassigned"}
        </Badge>
      </Group>

      <Card withBorder radius="md" p="lg">
        <Stack gap="sm">
          <Group justify="space-between">
            <Text fw={600}>Email</Text>
            <Text>{client.email}</Text>
          </Group>

          <Group justify="space-between">
            <Text fw={600}>Client ID</Text>
            <Text size="sm" c="dimmed">
              {client.id}
            </Text>
          </Group>

          <Group justify="space-between">
            <Text fw={600}>Created</Text>
            <Text>{new Date(client.created_at).toLocaleString()}</Text>
          </Group>

          <Group justify="space-between">
            <Text fw={600}>Last Updated</Text>
            <Text>{new Date(client.updated_at).toLocaleString()}</Text>
          </Group>
        </Stack>
      </Card>

      {/* ClientNotes Section */}
      <ClientNotesSection clientId={id} />
    </Stack>
  );
}
