import { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Text,
    Button,
    Stack,
    Group,
    Modal,
    TextInput,
    Textarea,
    NumberInput,
    Radio,
    Loader,
    Card,
    Title,
    Badge,
    ActionIcon,
    Accordion,
    ScrollArea,
    Divider,
    Select,
} from '@mantine/core';
import {
    IconStarFilled,
    IconTrash,
    IconEdit,
    IconPlus,
    IconClipboard,
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { apiService } from '../../services/api';
import classes from './AnswerEvaluation.module.css';

export function AnswerEvaluation() {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [evaluations, setEvaluations] = useState({});
    const [loading, setLoading] = useState(true);
    const [loadingQuestions, setLoadingQuestions] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [saving, setSaving] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        if_answer: 1,
        technical_accuracy: null,
        practical_utility: null,
        trustworthiness: null,
        comprehension_depth: null,
        issues_found: '',
        suggestions_for_improvement: '',
    });

    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        try {
            setLoading(true);
            const data = await apiService.getConversations(100, 0);
            // API returns structured object with conversations array
            setConversations(data.conversations || []);
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to load conversations',
                color: 'red',
            });
            console.error('Load conversations error:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadQuestionsForConversation = async (conversationId) => {
        try {
            setLoadingQuestions(true);
            setSelectedConversation(conversationId);

            // Get questions for this conversation
            const queriesData = await apiService.getConversationQueries(conversationId);
            setQuestions(queriesData.queries || []);

            // Load all evaluations
            const evalData = await apiService.getAllAnswerEvaluations();
            const evaluationsMap = {};
            (evalData.evaluations || []).forEach((evaluation) => {
                evaluationsMap[evaluation.evaluate_queryquestion_id] = evaluation;
            });
            setEvaluations(evaluationsMap);
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to load questions',
                color: 'red',
            });
            console.error('Load questions error:', error);
        } finally {
            setLoadingQuestions(false);
        }
    };

    const openCreateModal = (question) => {
        setCurrentQuestion(question);
        setIsEditing(false);
        setFormData({
            if_answer: question.answer ? 1 : 0,
            technical_accuracy: null,
            practical_utility: null,
            trustworthiness: null,
            comprehension_depth: null,
            issues_found: '',
            suggestions_for_improvement: '',
        });
        setModalOpen(true);
    };

    const openEditModal = (question, evaluation) => {
        setCurrentQuestion(question);
        setIsEditing(true);
        setFormData({
            if_answer: evaluation.if_answer,
            technical_accuracy: evaluation.technical_accuracy,
            practical_utility: evaluation.practical_utility,
            trustworthiness: evaluation.trustworthiness,
            comprehension_depth: evaluation.comprehension_depth,
            issues_found: evaluation.issues_found || '',
            suggestions_for_improvement: evaluation.suggestions_for_improvement || '',
        });
        setModalOpen(true);
    };

    const handleSave = async () => {
        if (!currentQuestion) return;

        try {
            setSaving(true);

            const evaluationData = {
                evaluate_queryquestion_id: currentQuestion.id,
                ...formData,
            };

            if (isEditing) {
                const evaluation = evaluations[currentQuestion.id];
                await apiService.updateAnswerEvaluation(evaluation.id, evaluationData);
                notifications.show({
                    title: 'Success',
                    message: 'Evaluation updated successfully',
                    color: 'green',
                });
            } else {
                await apiService.createAnswerEvaluation(evaluationData);
                notifications.show({
                    title: 'Success',
                    message: 'Evaluation created successfully',
                    color: 'green',
                });
            }

            if (selectedConversation) {
                await loadQuestionsForConversation(selectedConversation);
            }
            setModalOpen(false);
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: error.message || 'Failed to save evaluation',
                color: 'red',
            });
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (questionId) => {
        const evaluation = evaluations[questionId];
        if (!evaluation) return;

        try {
            await apiService.deleteAnswerEvaluation(evaluation.id);
            notifications.show({
                title: 'Success',
                message: 'Evaluation deleted successfully',
                color: 'green',
            });
            if (selectedConversation) {
                await loadQuestionsForConversation(selectedConversation);
            }
        } catch (error) {
            notifications.show({
                title: 'Error',
                message: 'Failed to delete evaluation',
                color: 'red',
            });
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleString();
    };

    const renderStars = (rating) => {
        if (!rating) return <Text size="sm" c="dimmed">Not rated</Text>;
        return (
            <Group gap={2}>
                {[...Array(5)].map((_, i) => (
                    <IconStarFilled
                        key={i}
                        size={14}
                        style={{
                            color: i < Math.round(rating) ? '#ffd43b' : '#e0e0e0',
                        }}
                    />
                ))}
                <Text size="sm" ml={4}>{rating.toFixed(1)}</Text>
            </Group>
        );
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
                        <IconClipboard size={24} />
                        <Title order={2}>Answer Evaluations</Title>
                    </Group>
                    <Group>
                        {selectedConversation && (
                            <Badge size="lg" variant="light">
                                {questions.length} Questions
                            </Badge>
                        )}
                        <Badge size="lg" variant="outline">
                            {conversations.length} Conversations
                        </Badge>
                    </Group>
                </Group>
            </Paper>

            {/* Conversation Selector */}
            <Paper p="md" shadow="sm">
                <Select
                    label="Select Conversation"
                    placeholder="Choose a conversation to view questions"
                    data={conversations.map(conv => ({
                        value: String(conv.id),
                        label: `Conversation #${conv.id} - ${formatDate(conv.created_at)}`,
                    }))}
                    value={selectedConversation ? String(selectedConversation) : null}
                    onChange={(value) => value && loadQuestionsForConversation(parseInt(value))}
                    searchable
                    clearable
                    size="md"
                />
            </Paper>

            {/* Questions List */}
            <ScrollArea className={classes.scrollArea}>
                <Stack gap="md" p="md">
                    {!selectedConversation ? (
                        <Card p="xl" className={classes.emptyState}>
                            <Stack align="center" gap="md">
                                <IconClipboard size={48} stroke={1.5} />
                                <Text size="lg" fw={500}>Select a Conversation</Text>
                                <Text c="dimmed" ta="center">
                                    Choose a conversation from the dropdown above to view and evaluate its questions.
                                </Text>
                            </Stack>
                        </Card>
                    ) : loadingQuestions ? (
                        <Group justify="center" mt="xl">
                            <Loader size="lg" />
                        </Group>
                    ) : questions.length === 0 ? (
                        <Card p="xl" className={classes.emptyState}>
                            <Stack align="center" gap="md">
                                <IconClipboard size={48} stroke={1.5} />
                                <Text size="lg" fw={500}>No Questions Found</Text>
                                <Text c="dimmed" ta="center">
                                    This conversation has no questions yet.
                                </Text>
                            </Stack>
                        </Card>
                    ) : (
                        <Accordion variant="separated" radius="md">
                            {questions.map((question) => {
                                const evaluation = evaluations[question.id];
                                const hasEvaluation = !!evaluation;

                                return (
                                    <Accordion.Item key={question.id} value={`q-${question.id}`}>
                                        <Accordion.Control>
                                            <Group justify="space-between" wrap="nowrap">
                                                <Box style={{ flex: 1 }}>
                                                    <Group gap="xs" mb={4}>
                                                        <Badge size="sm" variant="outline">
                                                            Q#{question.id}
                                                        </Badge>
                                                        {hasEvaluation && (
                                                            <Badge size="sm" color="green">
                                                                Evaluated
                                                            </Badge>
                                                        )}
                                                    </Group>
                                                    <Text fw={500} lineClamp={2}>
                                                        {question.question}
                                                    </Text>
                                                    <Text size="xs" c="dimmed" mt={4}>
                                                        {formatDate(question.send_time)}
                                                    </Text>
                                                </Box>
                                            </Group>
                                        </Accordion.Control>

                                        <Accordion.Panel>
                                            <Stack gap="md">
                                                {/* Question Details */}
                                                <Box>
                                                    <Group justify="space-between" mb="xs">
                                                        <Text size="sm" fw={500}>Answer:</Text>
                                                        {question.thinktime !== null && question.thinktime !== undefined && (
                                                            <Badge variant="light" color="blue" size="sm">
                                                                Think Time: {question.thinktime.toFixed(2)}s
                                                            </Badge>
                                                        )}
                                                    </Group>
                                                    <Text size="sm" c="dimmed">
                                                        {question.answer || 'No answer provided'}
                                                    </Text>
                                                </Box>

                                                <Divider />

                                                {/* Evaluation Display or Create Button */}
                                                {hasEvaluation ? (
                                                    <>
                                                        <Box>
                                                            <Group justify="space-between" mb="md">
                                                                <Text size="sm" fw={600}>Evaluation Metrics</Text>
                                                                <Group gap="xs">
                                                                    <ActionIcon
                                                                        variant="light"
                                                                        color="blue"
                                                                        onClick={() => openEditModal(question, evaluation)}
                                                                    >
                                                                        <IconEdit size={16} />
                                                                    </ActionIcon>
                                                                    <ActionIcon
                                                                        variant="light"
                                                                        color="red"
                                                                        onClick={() => handleDelete(question.id)}
                                                                    >
                                                                        <IconTrash size={16} />
                                                                    </ActionIcon>
                                                                </Group>
                                                            </Group>

                                                            <Stack gap="xs">
                                                                <Group justify="space-between">
                                                                    <Text size="sm">Answer Provided:</Text>
                                                                    <Badge color={evaluation.if_answer ? 'green' : 'red'}>
                                                                        {evaluation.if_answer ? 'Yes' : 'No'}
                                                                    </Badge>
                                                                </Group>

                                                                <Group justify="space-between">
                                                                    <Text size="sm">Technical Accuracy:</Text>
                                                                    {renderStars(evaluation.technical_accuracy)}
                                                                </Group>

                                                                <Group justify="space-between">
                                                                    <Text size="sm">Practical Utility:</Text>
                                                                    {renderStars(evaluation.practical_utility)}
                                                                </Group>

                                                                <Group justify="space-between">
                                                                    <Text size="sm">Trustworthiness:</Text>
                                                                    {renderStars(evaluation.trustworthiness)}
                                                                </Group>

                                                                <Group justify="space-between">
                                                                    <Text size="sm">Comprehension Depth:</Text>
                                                                    {renderStars(evaluation.comprehension_depth)}
                                                                </Group>

                                                                {evaluation.issues_found && (
                                                                    <Box mt="xs">
                                                                        <Text size="sm" fw={500}>Issues Found:</Text>
                                                                        <Text size="sm" c="dimmed">{evaluation.issues_found}</Text>
                                                                    </Box>
                                                                )}

                                                                {evaluation.suggestions_for_improvement && (
                                                                    <Box mt="xs">
                                                                        <Text size="sm" fw={500}>Suggestions:</Text>
                                                                        <Text size="sm" c="dimmed">{evaluation.suggestions_for_improvement}</Text>
                                                                    </Box>
                                                                )}

                                                                <Text size="xs" c="dimmed" mt="xs">
                                                                    Created: {formatDate(evaluation.created_at)}
                                                                </Text>
                                                            </Stack>
                                                        </Box>
                                                    </>
                                                ) : (
                                                    <Button
                                                        leftSection={<IconPlus size={16} />}
                                                        onClick={() => openCreateModal(question)}
                                                    >
                                                        Create Evaluation
                                                    </Button>
                                                )}
                                            </Stack>
                                        </Accordion.Panel>
                                    </Accordion.Item>
                                );
                            })}
                        </Accordion>
                    )}
                </Stack>
            </ScrollArea>

            {/* Evaluation Modal */}
            <Modal
                opened={modalOpen}
                onClose={() => setModalOpen(false)}
                title={isEditing ? 'Edit Evaluation' : 'Create Evaluation'}
                size="lg"
                centered
            >
                <Stack gap="md">
                    <Box>
                        <Text size="sm" fw={500} mb={4}>Question:</Text>
                        <Text size="sm" c="dimmed">{currentQuestion?.question}</Text>
                    </Box>

                    <Divider />

                    <Radio.Group
                        label="Was an answer provided?"
                        value={String(formData.if_answer)}
                        onChange={(value) => setFormData({ ...formData, if_answer: parseInt(value) })}
                    >
                        <Group mt="xs">
                            <Radio value="1" label="Yes" />
                            <Radio value="0" label="No" />
                        </Group>
                    </Radio.Group>

                    <NumberInput
                        label="Technical Accuracy (1-5)"
                        placeholder="Rate 1-5"
                        min={1}
                        max={5}
                        step={0.1}
                        decimalScale={1}
                        value={formData.technical_accuracy}
                        onChange={(value) => setFormData({ ...formData, technical_accuracy: value })}
                    />

                    <NumberInput
                        label="Practical Utility (1-5)"
                        placeholder="Rate 1-5"
                        min={1}
                        max={5}
                        step={0.1}
                        decimalScale={1}
                        value={formData.practical_utility}
                        onChange={(value) => setFormData({ ...formData, practical_utility: value })}
                    />

                    <NumberInput
                        label="Trustworthiness (1-5)"
                        placeholder="Rate 1-5"
                        min={1}
                        max={5}
                        step={0.1}
                        decimalScale={1}
                        value={formData.trustworthiness}
                        onChange={(value) => setFormData({ ...formData, trustworthiness: value })}
                    />

                    <NumberInput
                        label="Comprehension Depth (1-5)"
                        placeholder="Rate 1-5"
                        min={1}
                        max={5}
                        step={0.1}
                        decimalScale={1}
                        value={formData.comprehension_depth}
                        onChange={(value) => setFormData({ ...formData, comprehension_depth: value })}
                    />

                    <Textarea
                        label="Issues Found"
                        placeholder="Describe any issues found in the answer"
                        minRows={3}
                        value={formData.issues_found}
                        onChange={(e) => setFormData({ ...formData, issues_found: e.target.value })}
                    />

                    <Textarea
                        label="Suggestions for Improvement"
                        placeholder="Provide suggestions to improve the answer"
                        minRows={3}
                        value={formData.suggestions_for_improvement}
                        onChange={(e) => setFormData({ ...formData, suggestions_for_improvement: e.target.value })}
                    />

                    <Group justify="flex-end" gap="sm" mt="md">
                        <Button variant="outline" onClick={() => setModalOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleSave} loading={saving}>
                            {isEditing ? 'Update' : 'Save'}
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Box>
    );
}

