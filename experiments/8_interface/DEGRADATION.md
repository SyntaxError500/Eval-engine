# Phase 8 degradation checks

## judge rate-limited: PASS

Expected: queued with 'evaluating…', no other model grades it; graded on retry

- first_attempt: queued
- error: QuotaExhausted: gemini#c2a56912/gemini-3.5-flash-lite: daily limit of 1 requests reached (2026-11-06)
- other_models_called: 0
- after_retry: done
- graded_by: gemini/gemini-3.5-flash-lite

## verifier down: PASS

Expected: graded on the original rubric, amendment error in the trace

- status: done
- amendment_fired: True
- amendment_error: ProviderError: groq 404: Error code: 404 - {'error': {'message': 'The model `qwen/model-that-does-not-exist` does not exist or you do not have access to it.', 'type': 'invalid_request_error', 'code': 'model_not_found'}}
- rubric_used: generated

## feedback model down: PASS

Expected: graded, with template feedback marked as such

- status: done
- feedback_sources: ['template']
- fallbacks: ['feedback model unavailable: ProviderError']

