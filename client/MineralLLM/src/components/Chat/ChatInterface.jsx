import { useState, useEffect, useRef } from 'react';
import {
    Box,
    Paper,
    Text,
    TextInput,
    Button,
    ScrollArea,
    Group,
    Stack,
    Select,
    ActionIcon,
    Loader,
    Alert,
    Divider,
    Modal,
} from '@mantine/core';
import { IconSend, IconPlus, IconUser, IconRobot, IconInfoCircle, IconDiamond, IconTrash } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import classes from './ChatInterface.module.css';

const API_BASE_URL = 'http://localhost:3000';

export function ChatInterface() {
    const [conversations, setConversations] = useState([]);
    const [currentConversationId, setCurrentConversationId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [modelName, setModelName] = useState('qwen2.5:7b');
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [conversationToDelete, setConversationToDelete] = useState(null);
    const scrollAreaRef = useRef();

    const scrollToBottom = () => {
        if (scrollAreaRef.current) {
            scrollAreaRef.current.scrollTo({ top: scrollAreaRef.current.scrollHeight, behavior: 'smooth' });
        }
    };

    useEffect(() => {
        loadConversations();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const loadConversations = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/v1/conversation/conversations`);
            if (response.ok) {
                const data = await response.json();
                // API now returns structured object with conversations array
                const conversationsList = data.conversations || [];
                setConversations(conversationsList);
                if (conversationsList.length > 0 && !currentConversationId) {
                    setCurrentConversationId(conversationsList[0].id);
                    loadConversationHistory(conversationsList[0].id);
                }
            }
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
    };

    const loadConversationHistory = async (conversationId) => {
        if (!conversationId) return;

        try {
            const response = await fetch(`${API_BASE_URL}/v1/conversation/conversation/${conversationId}/queries`);
            if (response.ok) {
                const data = await response.json();
                const historyMessages = [];

                data.queries.forEach(query => {
                    // Add user message
                    historyMessages.push({
                        type: 'user',
                        content: query.question,
                        timestamp: new Date(query.send_time),
                    });

                    // Add assistant message if there's an answer
                    if (query.answer) {
                        const sources = query.sourcetrace ? query.sourcetrace.split('\n').filter(s => s.trim()) : [];
                        historyMessages.push({
                            type: 'assistant',
                            content: query.answer,
                            sources: sources,
                            timestamp: new Date(query.finish_time || query.send_time),
                        });
                    }
                });

                setMessages(historyMessages);
            }
        } catch (error) {
            console.error('Failed to load conversation history:', error);
            setMessages([]);
        }
    };

    const createNewConversation = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/v1/conversation/conversation`, {
                method: 'POST',
            });
            if (response.ok) {
                const data = await response.json();
                setCurrentConversationId(data.id);
                setMessages([]); // Clear messages for new conversation
                await loadConversations();
                notifications.show({
                    title: 'Success',
                    message: 'New conversation created',
                    color: 'green',
                });
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to create conversation',
                color: 'red',
            });
        }
    };

    const deleteConversation = async () => {
        if (!conversationToDelete) return;

        try {
            const response = await fetch(`${API_BASE_URL}/v1/conversation/conversation/${conversationToDelete.id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                // Remove from conversations list
                const updatedConversations = conversations.filter(conv => conv.id !== conversationToDelete.id);
                setConversations(updatedConversations);

                // If we deleted the current conversation, switch to another one or clear
                if (currentConversationId === conversationToDelete.id) {
                    if (updatedConversations.length > 0) {
                        const newConversationId = updatedConversations[0].id;
                        setCurrentConversationId(newConversationId);
                        loadConversationHistory(newConversationId);
                    } else {
                        setCurrentConversationId(null);
                        setMessages([]);
                    }
                }

                notifications.show({
                    title: 'Success',
                    message: 'Conversation deleted successfully',
                    color: 'green',
                });
            } else {
                throw new Error('Failed to delete conversation');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to delete conversation',
                color: 'red',
            });
        } finally {
            setDeleteModalOpen(false);
            setConversationToDelete(null);
        }
    };

    const sendMessage = async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMessage = { type: 'user', content: inputValue, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/v1/query/send_query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conversation_id: currentConversationId || 0,
                    query: userMessage.content,
                    model_name: modelName,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                const assistantMessage = {
                    type: 'assistant',
                    content: data.answer,
                    sources: data.sources || [],
                    timestamp: new Date(),
                };
                setMessages(prev => [...prev, assistantMessage]);

                // If conversation was auto-created, reload conversations
                if (!currentConversationId) {
                    await loadConversations();
                    // The response should contain the conversation_id if it was auto-created
                    // You may need to set currentConversationId from the response
                }
            } else {
                throw new Error('Failed to send query');
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to send message',
                color: 'red',
            });
            setMessages(prev => [...prev, {
                type: 'error',
                content: 'Sorry, I encountered an error processing your request.',
                timestamp: new Date(),
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    };

    const formatTime = (timestamp) => {
        return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <Box className={classes.container}>
            {/* Header */}
            <Paper p="md" shadow="sm" className={classes.header}>
                <Group justify="space-between">
                    <Group>
                        <Text size="lg" fw={600}>Mineral Exploration Assistant</Text>
                        <Group gap="xs">
                            <Select
                                value={currentConversationId?.toString() || ''}
                                onChange={(value) => {
                                    const newConversationId = parseInt(value);
                                    setCurrentConversationId(newConversationId);
                                    loadConversationHistory(newConversationId);
                                }}
                                data={conversations.map(conv => ({
                                    value: conv.id.toString(),
                                    label: `Conversation ${conv.id} - ${new Date(conv.created_at).toLocaleDateString()}`,
                                }))}
                                placeholder="Select conversation"
                                w={200}
                            />
                            {currentConversationId && (
                                <ActionIcon
                                    color="red"
                                    variant="subtle"
                                    onClick={() => {
                                        const conversation = conversations.find(conv => conv.id === currentConversationId);
                                        if (conversation) {
                                            setConversationToDelete(conversation);
                                            setDeleteModalOpen(true);
                                        }
                                    }}
                                    title="Delete conversation"
                                >
                                    <IconTrash size={16} />
                                </ActionIcon>
                            )}
                        </Group>
                    </Group>

                    <Group>
                        <Select
                            value={modelName}
                            onChange={setModelName}
                            data={[
                                { value: 'qwen2.5:7b', label: 'Qwen 2.5 7B' },
                                { value: 'llama3.1:8b', label: 'Llama 3.1 8B' },
                            ]}
                            w={150}
                        />
                        <Button
                            leftSection={<IconPlus size={16} />}
                            onClick={createNewConversation}
                            variant="light"
                        >
                            New Chat
                        </Button>
                    </Group>
                </Group>
            </Paper>

            {/* Messages Area */}
            <ScrollArea
                className={classes.messagesArea}
                viewportRef={scrollAreaRef}
            >
                <Stack gap="md" p="md">
                    {messages.length === 0 ? (
                        <Paper p="xl" className={classes.welcomeMessage}>
                            <Stack align="center" gap="md">
                                <IconDiamond size={48} stroke={1.5} />
                                <Text size="lg" fw={500}>Welcome to Mineral Exploration Assistant</Text>
                                <Text c="dimmed" ta="center">
                                    Ask me anything about geological formations, mineral deposits, or upload documents to expand my knowledge base.
                                </Text>
                            </Stack>
                        </Paper>
                    ) : (
                        messages.map((message, index) => (
                            <div key={index} className={classes.messageWrapper}>
                                <Group align="flex-start" gap="sm" className={
                                    message.type === 'user' ? classes.userMessage : classes.assistantMessage
                                }>
                                    <div className={classes.avatar}>
                                        {message.type === 'user' ? (
                                            <IconUser size={20} />
                                        ) : (
                                            <IconRobot size={20} />
                                        )}
                                    </div>

                                    <Stack gap="xs" style={{ flex: 1 }}>
                                        <Paper p="md" className={classes.messageBubble}>
                                            <Text style={{ whiteSpace: 'pre-wrap' }}>{message.content}</Text>

                                            {message.sources && message.sources.length > 0 && (
                                                <>
                                                    <Divider my="sm" />
                                                    <Alert icon={<IconInfoCircle size={16} />} title="Sources" variant="light">
                                                        <Stack gap="xs">
                                                            {message.sources.map((source, idx) => (
                                                                <Text key={idx} size="sm" c="dimmed">
                                                                    {source.substring(0, 200)}...
                                                                </Text>
                                                            ))}
                                                        </Stack>
                                                    </Alert>
                                                </>
                                            )}
                                        </Paper>

                                        <Text size="xs" c="dimmed" className={classes.timestamp}>
                                            {formatTime(message.timestamp)}
                                        </Text>
                                    </Stack>
                                </Group>
                            </div>
                        ))
                    )}

                    {isLoading && (
                        <Group align="flex-start" gap="sm" className={classes.assistantMessage}>
                            <div className={classes.avatar}>
                                <IconRobot size={20} />
                            </div>
                            <Paper p="md" className={classes.messageBubble}>
                                <Group gap="xs">
                                    <Loader size="sm" />
                                    <Text c="dimmed">Thinking...</Text>
                                </Group>
                            </Paper>
                        </Group>
                    )}
                </Stack>
            </ScrollArea>

            {/* Input Area */}
            <Paper p="md" shadow="sm" className={classes.inputArea}>
                <Group gap="sm">
                    <TextInput
                        flex={1}
                        placeholder="Ask about geological formations, mineral deposits..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isLoading}
                    />
                    <ActionIcon
                        size="lg"
                        onClick={sendMessage}
                        disabled={!inputValue.trim() || isLoading}
                        variant="filled"
                    >
                        <IconSend size={18} />
                    </ActionIcon>
                </Group>
            </Paper>

            {/* Delete Conversation Confirmation Modal */}
            <Modal
                opened={deleteModalOpen}
                onClose={() => setDeleteModalOpen(false)}
                title="Delete Conversation"
                centered
            >
                <Stack>
                    <Text>
                        Are you sure you want to delete this conversation? This action cannot be undone and will permanently remove all messages in this conversation.
                    </Text>

                    {conversationToDelete && (
                        <Text size="sm" c="dimmed">
                            Conversation {conversationToDelete.id} - {new Date(conversationToDelete.created_at).toLocaleDateString()}
                        </Text>
                    )}

                    <Group justify="flex-end" gap="sm">
                        <Button variant="outline" onClick={() => setDeleteModalOpen(false)}>
                            Cancel
                        </Button>
                        <Button color="red" onClick={deleteConversation}>
                            Delete
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Box>
    );
}
