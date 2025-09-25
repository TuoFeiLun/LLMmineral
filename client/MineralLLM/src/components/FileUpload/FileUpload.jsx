import { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Text,
    Button,
    Stack,
    Group,
    Badge,
    ActionIcon,
    Card,
    Title,
    Alert,
    Loader,
    Progress,
    Table,
} from '@mantine/core';
import {
    IconUpload,
    IconFile,
    IconTrash,
    IconDownload,
    IconInfoCircle,
    IconFileText,
    IconPhoto,
    IconFileSpreadsheet,
} from '@tabler/icons-react';
import { Dropzone, MIME_TYPES } from '@mantine/dropzone';
import { notifications } from '@mantine/notifications';
import classes from './FileUpload.module.css';

const API_BASE_URL = 'http://localhost:3000';

const SUPPORTED_TYPES = [
    MIME_TYPES.pdf,
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // docx
    MIME_TYPES.csv,
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // xlsx
    MIME_TYPES.json,
    'text/plain',
    MIME_TYPES.png,
    MIME_TYPES.jpeg,
    'image/tiff',
    'image/tif',
];

const getFileIcon = (fileType) => {
    if (fileType.includes('pdf') || fileType.includes('doc')) return IconFileText;
    if (fileType.includes('image')) return IconPhoto;
    if (fileType.includes('spreadsheet') || fileType.includes('csv')) return IconFileSpreadsheet;
    return IconFile;
};

const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export function FileUpload() {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    useEffect(() => {
        loadFiles();
    }, []);

    const loadFiles = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE_URL}/v1/kb/corpus_files`);
            if (response.ok) {
                const data = await response.json();
                setFiles(data.corpus_files || []);
            } else {
                throw new Error('Failed to load files');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to load files',
                color: 'red',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (uploadedFiles) => {
        if (uploadedFiles.length === 0) return;

        setUploading(true);
        setUploadProgress(0);

        try {
            for (let i = 0; i < uploadedFiles.length; i++) {
                const file = uploadedFiles[i];
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch(`${API_BASE_URL}/v1/kb/corpus_files`, {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    const result = await response.json();
                    notifications.show({
                        title: 'Success',
                        message: `${result.file_name} uploaded successfully`,
                        color: 'green',
                    });
                } else {
                    const error = await response.json();
                    throw new Error(error.detail || `Failed to upload ${file.name}`);
                }

                setUploadProgress(((i + 1) / uploadedFiles.length) * 100);
            }

            await loadFiles();
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: error.message,
                color: 'red',
            });
        } finally {
            setUploading(false);
            setUploadProgress(0);
        }
    };

    const deleteFile = async (fileId, fileName) => {
        try {
            const response = await fetch(`${API_BASE_URL}/v1/kb/corpus_files/${fileId}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                await loadFiles();
                notifications.show({
                    title: 'Success',
                    message: `${fileName} deleted successfully`,
                    color: 'green',
                });
            } else {
                throw new Error('Failed to delete file');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to delete file',
                color: 'red',
            });
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
                        <IconUpload size={24} />
                        <Title order={2}>Knowledge Base Files</Title>
                    </Group>
                    <Badge variant="outline" size="lg">
                        {files.length} files
                    </Badge>
                </Group>
            </Paper>

            <Stack gap="md" p="md">
                {/* Upload Area */}
                <Card p="md" className={classes.uploadCard}>
                    <Stack gap="md">
                        <Alert icon={<IconInfoCircle size={16} />} variant="light">
                            <Text size="sm">
                                Upload documents to expand the AI's knowledge base. Supported formats: PDF, DOCX, TXT, JSON, CSV, XLSX, and images (TIFF, JPG, PNG).
                                Maximum file size: 50MB.
                            </Text>
                        </Alert>

                        <Dropzone
                            onDrop={handleFileUpload}
                            accept={SUPPORTED_TYPES}
                            maxSize={50 * 1024 * 1024} // 50MB
                            disabled={uploading}
                            className={classes.dropzone}
                        >
                            <Group justify="center" gap="xl" mih={220} style={{ pointerEvents: 'none' }}>
                                <Dropzone.Accept>
                                    <IconUpload size={52} stroke={1.5} />
                                </Dropzone.Accept>
                                <Dropzone.Reject>
                                    <IconFile size={52} stroke={1.5} />
                                </Dropzone.Reject>
                                <Dropzone.Idle>
                                    <IconUpload size={52} stroke={1.5} />
                                </Dropzone.Idle>

                                <div>
                                    <Text size="xl" inline>
                                        Drag files here or click to select
                                    </Text>
                                    <Text size="sm" c="dimmed" inline mt={7}>
                                        Upload geological documents, research papers, or data files
                                    </Text>
                                </div>
                            </Group>
                        </Dropzone>

                        {uploading && (
                            <Stack gap="xs">
                                <Group justify="space-between">
                                    <Text size="sm">Uploading files...</Text>
                                    <Text size="sm">{Math.round(uploadProgress)}%</Text>
                                </Group>
                                <Progress value={uploadProgress} animated />
                            </Stack>
                        )}
                    </Stack>
                </Card>

                {/* Files List */}
                {files.length === 0 ? (
                    <Card p="xl" className={classes.emptyState}>
                        <Stack align="center" gap="md">
                            <IconFile size={48} stroke={1.5} />
                            <Text size="lg" fw={500}>No Files Uploaded</Text>
                            <Text c="dimmed" ta="center">
                                Upload your first document to start building the knowledge base for the AI assistant.
                            </Text>
                        </Stack>
                    </Card>
                ) : (
                    <Card p="md">
                        <Table striped highlightOnHover>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>File</Table.Th>
                                    <Table.Th>Type</Table.Th>
                                    <Table.Th>Size</Table.Th>
                                    <Table.Th>Uploaded</Table.Th>
                                    <Table.Th>Status</Table.Th>
                                    <Table.Th>Actions</Table.Th>
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {files.map((file) => {
                                    const FileIcon = getFileIcon(file.file_type);
                                    return (
                                        <Table.Tr key={file.id}>
                                            <Table.Td>
                                                <Group gap="sm">
                                                    <FileIcon size={20} />
                                                    <Text size="sm" fw={500}>
                                                        {file.file_name}
                                                    </Text>
                                                </Group>
                                            </Table.Td>
                                            <Table.Td>
                                                <Badge variant="outline" size="sm">
                                                    {file.file_type}
                                                </Badge>
                                            </Table.Td>
                                            <Table.Td>
                                                <Text size="sm">{formatFileSize(file.file_size)}</Text>
                                            </Table.Td>
                                            <Table.Td>
                                                <Text size="sm">{formatDate(file.created_at)}</Text>
                                            </Table.Td>
                                            <Table.Td>
                                                <Group gap="xs">
                                                    <Badge
                                                        color={file.file_exists ? 'green' : 'red'}
                                                        variant="light"
                                                        size="sm"
                                                    >
                                                        {file.file_exists ? 'Available' : 'Missing'}
                                                    </Badge>
                                                    {file.vectordatabase_id && (
                                                        <Badge color="blue" variant="light" size="sm">
                                                            Vectorized
                                                        </Badge>
                                                    )}
                                                </Group>
                                            </Table.Td>
                                            <Table.Td>
                                                <Group gap="xs">
                                                    <ActionIcon
                                                        variant="subtle"
                                                        color="red"
                                                        onClick={() => deleteFile(file.id, file.file_name)}
                                                    >
                                                        <IconTrash size={16} />
                                                    </ActionIcon>
                                                </Group>
                                            </Table.Td>
                                        </Table.Tr>
                                    );
                                })}
                            </Table.Tbody>
                        </Table>
                    </Card>
                )}
            </Stack>
        </Box>
    );
}
