import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000/api",
    timeout: 30000,
});

export const getProducts = async () => {
    const response = await api.get("/products/");
    return response.data;
};

export const getProduct = async (id) => {
    const response = await api.get(`/products/${id}/`);
    return response.data;
};

export const createProduct = async (formData) => {
    const response = await api.post("/products/", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    return response.data;
};

export const uploadBulkFile = async (formData) => {
    const response = await api.post("/bulk-upload/", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });

    return response.data;
};

export const getJobs = async () => {
    const response = await api.get("/jobs/");
    return response.data;
};

export const getJob = async (id) => {
    const response = await api.get(`/jobs/${id}/`);
    return response.data;
};

export const approveProductClassification = async (id, data = { approved: true }) => {
    const response = await api.post(`/products/${id}/approve/`, data);
    return response.data;
};

export default api;