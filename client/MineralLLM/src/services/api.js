const API_BASE_URL = 'http://localhost:3000';

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Request failed' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error: ${endpoint}`, error);
            throw error;
        }
    }

    // Conversation endpoints
    async createConversation() {
        return this.request('/v1/conversation/conversation', { method: 'POST' });
    }

    async getConversation(id) {
        return this.request(`/v1/conversation/conversation/${id}`);
    }

    async getConversationQueries(id) {
        return this.request(`/v1/conversation/conversation/${id}/queries`);
    }

    async getConversations(limit = 50, offset = 0) {
        return this.request(`/v1/conversation/conversations?limit=${limit}&offset=${offset}`);
    }

    async deleteConversation(id) {
        return this.request(`/v1/conversation/conversation/${id}`, { method: 'DELETE' });
    }

    // Query endpoints
    async sendQuery(conversationId, query, modelName = 'qwen2.5-7b', llmModelId = null) {
        return this.request('/v1/query/send_query', {
            method: 'POST',
            body: JSON.stringify({
                conversation_id: conversationId,
                query,
                model_name: modelName,
                llmmodel_id: llmModelId,
            }),
        });
    }

    // File management endpoints
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        return fetch(`${this.baseUrl}/v1/kb/corpus_files`, {
            method: 'POST',
            body: formData,
        }).then(response => {
            if (!response.ok) {
                return response.json().then(error => {
                    throw new Error(error.detail || 'Upload failed');
                });
            }
            return response.json();
        });
    }

    async getCorpusFiles(limit = 50, offset = 0) {
        return this.request(`/v1/kb/corpus_files?limit=${limit}&offset=${offset}`);
    }

    async getCorpusFile(id) {
        return this.request(`/v1/kb/corpus_files/${id}`);
    }

    async deleteCorpusFile(id) {
        return this.request(`/v1/kb/corpus_files/${id}`, { method: 'DELETE' });
    }

    async createVectorCollection(collectionName) {
        return this.request('/v1/kb/corpus_files_to_vector_database', {
            method: 'POST',
            body: JSON.stringify({ collection_name: collectionName }),
        });
    }

    // RAG/Collection endpoints
    async getCollections() {
        return this.request('/v1/rag/collection');
    }

    async getActiveCollections() {
        return this.request('/v1/rag/collection/active');
    }

    async getCollection(name) {
        return this.request(`/v1/rag/collection/${name}`);
    }

    async updateCollectionStatus(collectionName, usingStatus) {
        return this.request('/v1/rag/collection/status', {
            method: 'POST',
            body: JSON.stringify({
                collection_name: collectionName,
                using_status: usingStatus,
            }),
        });
    }

    async deleteCollection(name) {
        return this.request(`/v1/rag/collection/${name}`, { method: 'DELETE' });
    }

    // Answer Evaluation endpoints
    async createAnswerEvaluation(evaluationData) {
        return this.request('/v1/evaluation/answer_evaluation', {
            method: 'POST',
            body: JSON.stringify(evaluationData),
        });
    }

    async getAnswerEvaluation(evaluationId) {
        return this.request(`/v1/evaluation/answer_evaluation/${evaluationId}`);
    }

    async getAnswerEvaluationByQuestion(questionId) {
        return this.request(`/v1/evaluation/answer_evaluation/question/${questionId}`);
    }

    async getAllAnswerEvaluations() {
        return this.request('/v1/evaluation/answer_evaluations');
    }

    async updateAnswerEvaluation(evaluationId, evaluationData) {
        return this.request(`/v1/evaluation/answer_evaluation/${evaluationId}`, {
            method: 'PATCH',
            body: JSON.stringify(evaluationData),
        });
    }

    async deleteAnswerEvaluation(evaluationId) {
        return this.request(`/v1/evaluation/answer_evaluation/${evaluationId}`, {
            method: 'DELETE',
        });
    }
}

export const apiService = new ApiService();
export default apiService;
