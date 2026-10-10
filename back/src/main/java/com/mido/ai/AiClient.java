package com.mido.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.mido.global.exception.ApiException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

/**
 * FastAPI(AI 서버) 호출.
 *   POST /api/v1/analyze  의존성 위험 분석
 *   GET  /api/v1/owasp    OWASP Top 10 현황
 */
@Component
public class AiClient {

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public AiClient(RestTemplate restTemplate, @Value("${app.ai.base-url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl;
    }

    public JsonNode analyze(String manifest) {
        return post("/api/v1/analyze", Map.of("manifest", manifest));
    }

    public JsonNode owasp() {
        try {
            JsonNode response = restTemplate.getForObject(baseUrl + "/api/v1/owasp", JsonNode.class);
            if (response == null) {
                throw ApiException.aiError("AI 서버 응답이 비어 있습니다.", null);
            }
            return response;
        } catch (RestClientException e) {
            throw ApiException.aiError("AI 서버 호출에 실패했습니다.", e);
        }
    }

    private JsonNode post(String path, Map<String, Object> request) {
        try {
            JsonNode response = restTemplate.postForObject(baseUrl + path, request, JsonNode.class);
            if (response == null) {
                throw ApiException.aiError("AI 서버 응답이 비어 있습니다.", null);
            }
            return response;
        } catch (RestClientException e) {
            throw ApiException.aiError("AI 서버 호출에 실패했습니다.", e);
        }
    }
}
