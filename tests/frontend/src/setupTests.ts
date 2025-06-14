import '@testing-library/jest-dom';

// Mock do axios para testes
jest.mock('axios', () => ({
    create: jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn(),
        delete: jest.fn(),
    })),
}));

// Mock do OpenTelemetry
jest.mock('@opentelemetry/api', () => ({
    trace: {
        getTracer: jest.fn(() => ({
            startSpan: jest.fn(() => ({
                setAttributes: jest.fn(),
                recordException: jest.fn(),
                setStatus: jest.fn(),
                end: jest.fn(),
            })),
        })),
    },
}));
