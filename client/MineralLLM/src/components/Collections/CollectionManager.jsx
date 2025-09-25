import { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Text,
    Button,
    Stack,
    Group,
    Badge,
    Switch,
    ActionIcon,
    Modal,
    TextInput,
    Alert,
    Loader,
    Card,
    Title,
} from '@mantine/core';
import {
    IconDatabase,
    IconTrash,
    IconPlus,
    IconInfoCircle,
    IconCheck,
    IconX,
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import classes from './CollectionManager.module.css';

const API_BASE_URL = 'http://localhost:3000';

export function CollectionManager() {
    const [collections, setCollections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [collectionToDelete, setCollectionToDelete] = useState(null);
    const [createModalOpen, setCreateModalOpen] = useState(false);
    const [newCollectionName, setNewCollectionName] = useState('');
    const [creating, setCreating] = useState(false);

    useEffect(() => {
        loadCollections();
    }, []);

    const loadCollections = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE_URL}/v1/rag/collection`);
            if (response.ok) {
                const data = await response.json();
                setCollections(data.collections || []);
            } else {
                throw new Error('Failed to load collections');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to load collections',
                color: 'red',
            });
        } finally {
            setLoading(false);
        }
    };

    const toggleCollectionStatus = async (collectionName, currentStatus) => {
        try {
            const response = await fetch(`${API_BASE_URL}/v1/rag/collection/status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    collection_name: collectionName,
                    using_status: !currentStatus,
                }),
            });

            if (response.ok) {
                await loadCollections();
                notifications.show({
                    title: 'Success',
                    message: `Collection ${!currentStatus ? 'enabled' : 'disabled'}`,
                    color: 'green',
                });
            } else {
                throw new Error('Failed to update collection status');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to update collection status',
                color: 'red',
            });
        }
    };

    const deleteCollection = async () => {
        if (!collectionToDelete) return;

        try {
            const response = await fetch(
                `${API_BASE_URL}/v1/rag/collection/${collectionToDelete.collection_name}`,
                {
                    method: 'DELETE',
                }
            );

            if (response.ok) {
                await loadCollections();
                notifications.show({
                    title: 'Success',
                    message: 'Collection deleted successfully',
                    color: 'green',
                });
            } else {
                throw new Error('Failed to delete collection');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to delete collection',
                color: 'red',
            });
        } finally {
            setDeleteModalOpen(false);
            setCollectionToDelete(null);
        }
    };

    const createCollection = async () => {
        if (!newCollectionName.trim()) return;

        try {
            setCreating(true);
            const response = await fetch(`${API_BASE_URL}/v1/kb/corpus_files_to_vector_database`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    collection_name: newCollectionName.trim(),
                }),
            });

            if (response.ok) {
                await loadCollections();
                setCreateModalOpen(false);
                setNewCollectionName('');
                notifications.show({
                    title: 'Success',
                    message: 'Collection created successfully',
                    color: 'green',
                });
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create collection');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: error.message,
                color: 'red',
            });
        } finally {
            setCreating(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString([], {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    if (loading) {
        return (
            <Box className={classes.container}>
                <Group justify="center" mt="xl">
                    <Loader size="lg" />
                </Group>
            </Box>
        );
    }

    return (
        <Box className={classes.container}>
            {/* Header */}
            <Paper p="md" shadow="sm" className={classes.header}>
                <Group justify="space-between">
                    <Group>
                        <IconDatabase size={24} />
                        <Title order={2}>Vector Collections</Title>
                    </Group>
                    <Button
                        leftSection={<IconPlus size={16} />}
                        onClick={() => setCreateModalOpen(true)}
                    >
                        Create Collection
                    </Button>
                </Group>
            </Paper>

            {/* Collections List */}
            <Stack gap="md" p="md">
                <Alert icon={<IconInfoCircle size={16} />} variant="light">
                    <Text size="sm">
                        Vector collections store processed documents for AI querying. Enable collections to use them in chat responses.
                        Only enabled collections will be used for generating responses.
                    </Text>
                </Alert>

                {collections.length === 0 ? (
                    <Card p="xl" className={classes.emptyState}>
                        <Stack align="center" gap="md">
                            <IconDatabase size={48} stroke={1.5} />
                            <Text size="lg" fw={500}>No Collections Found</Text>
                            <Text c="dimmed" ta="center">
                                Create your first collection by uploading files and converting them to a vector database.
                            </Text>
                            <Button onClick={() => setCreateModalOpen(true)}>
                                Create Collection
                            </Button>
                        </Stack>
                    </Card>
                ) : (
                    collections.map((collection) => (
                        <Card key={collection.id} p="md" shadow="sm" className={classes.collectionCard}>
                            <Group justify="space-between" align="flex-start">
                                <Stack gap="xs" style={{ flex: 1 }}>
                                    <Group gap="sm">
                                        <Text fw={500} size="lg">{collection.collection_name}</Text>
                                        <Badge
                                            color={collection.using_status ? 'green' : 'gray'}
                                            variant={collection.using_status ? 'filled' : 'outline'}
                                        >
                                            {collection.using_status ? 'Active' : 'Inactive'}
                                        </Badge>
                                    </Group>

                                    <Text size="sm" c="dimmed">
                                        Created: {formatDate(collection.created_at)}
                                    </Text>

                                    <Text size="sm" c="dimmed">
                                        Path: {collection.db_path}
                                    </Text>
                                </Stack>

                                <Group gap="xs">
                                    <Switch
                                        checked={collection.using_status}
                                        onChange={() => toggleCollectionStatus(collection.collection_name, collection.using_status)}
                                        size="md"
                                        onLabel={<IconCheck size={12} />}
                                        offLabel={<IconX size={12} />}
                                    />

                                    <ActionIcon
                                        color="red"
                                        variant="subtle"
                                        onClick={() => {
                                            setCollectionToDelete(collection);
                                            setDeleteModalOpen(true);
                                        }}
                                    >
                                        <IconTrash size={16} />
                                    </ActionIcon>
                                </Group>
                            </Group>
                        </Card>
                    ))
                )}
            </Stack>

            {/* Delete Confirmation Modal */}
            <Modal
                opened={deleteModalOpen}
                onClose={() => setDeleteModalOpen(false)}
                title="Delete Collection"
                centered
            >
                <Stack>
                    <Text>
                        Are you sure you want to delete the collection "{collectionToDelete?.collection_name}"?
                        This action cannot be undone.
                    </Text>

                    <Group justify="flex-end" gap="sm">
                        <Button variant="outline" onClick={() => setDeleteModalOpen(false)}>
                            Cancel
                        </Button>
                        <Button color="red" onClick={deleteCollection}>
                            Delete
                        </Button>
                    </Group>
                </Stack>
            </Modal>

            {/* Create Collection Modal */}
            <Modal
                opened={createModalOpen}
                onClose={() => setCreateModalOpen(false)}
                title="Create New Collection"
                centered
            >
                <Stack>
                    <Text size="sm" c="dimmed">
                        Create a new vector collection from uploaded corpus files. Make sure you have uploaded files before creating a collection.
                    </Text>

                    <TextInput
                        label="Collection Name"
                        placeholder="Enter collection name"
                        value={newCollectionName}
                        onChange={(e) => setNewCollectionName(e.target.value)}
                        required
                    />

                    <Group justify="flex-end" gap="sm">
                        <Button variant="outline" onClick={() => setCreateModalOpen(false)}>
                            Cancel
                        </Button>
                        <Button
                            onClick={createCollection}
                            loading={creating}
                            disabled={!newCollectionName.trim()}
                        >
                            Create
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Box>
    );
}
