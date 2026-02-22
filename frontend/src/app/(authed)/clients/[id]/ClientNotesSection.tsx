"use client";

import { useEffect, useState } from "react";
import {
  Card,
  Group,
  Stack,
  Text,
  Textarea,
  Title,
  Button,
} from "@mantine/core";

import { useApi } from "@/api/context";
import { ClientNote } from "@/types/clients";

interface Props {
  clientId: string;
}

export default function ClientNotesSection({ clientId }: Props) {
  const api = useApi();

  const [notes, setNotes] = useState<ClientNote[]>([]);
  const [noteContent, setNoteContent] = useState("");
  const [notesLoading, setNotesLoading] = useState(true);

  //feat: fetch Notes
  useEffect(() => {
    setNotesLoading(true);

    api.clients
      .listClientNotes(clientId)
      .then(setNotes)
      .catch((err) => {
        console.error("Failed to fetch notes", err);
        setNotes([]);
      })
      .finally(() => setNotesLoading(false));
  }, [api, clientId]);

  //feat: create Note
  async function handleAddNote() {
    if (!noteContent.trim()) return;

    try {
      const newNote = await api.clients.createClientNote(
        clientId,
        noteContent.trim(),
      );

      setNotes((prev) => [newNote, ...prev]);
      setNoteContent("");
    } catch (err) {
      console.error("Failed to create note", err);
    }
  }

  return (
    <Card withBorder radius="md" p="lg">
      <Stack gap="md">
        <Title order={4}>Notes</Title>

        <Textarea
          placeholder="Add a note about this client..."
          value={noteContent}
          onChange={(e) => setNoteContent(e.currentTarget.value)}
          minRows={2}
          onKeyDown={(e) => {
            //feat: use CTRL + Enter to submit note
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              handleAddNote();
            }
          }}
        />

        <Group justify="flex-end">
          <Button onClick={handleAddNote} disabled={!noteContent.trim()}>
            Add Note
          </Button>
        </Group>

        {notesLoading ? (
          <Text size="sm" c="dimmed">
            Loading notes...
          </Text>
        ) : (
          <Stack gap="sm" mah={300} style={{ overflowY: "auto" }}>
            {notes.length === 0 ? (
              <Text size="sm" c="dimmed">
                No notes yet. Add the first one.
              </Text>
            ) : (
              notes.map((note) => (
                <Card key={note.id} withBorder radius="sm" p="sm">
                  <Stack gap={4}>
                    <Text size="sm">{note.content}</Text>
                    <Text size="xs" c="dimmed">
                      {note.user_id} ·{" "}
                      {new Date(note.created_at).toLocaleString()}
                    </Text>
                  </Stack>
                </Card>
              ))
            )}
          </Stack>
        )}
      </Stack>
    </Card>
  );
}
