package com.mido.owasp;

import com.fasterxml.jackson.databind.JsonNode;
import com.mido.ai.AiClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 기능 2: OWASP Top 10 공공데이터 현황. GET /api/owasp */
@RestController
@RequestMapping("/api/owasp")
public class OwaspController {

    private final AiClient aiClient;

    public OwaspController(AiClient aiClient) {
        this.aiClient = aiClient;
    }

    @GetMapping
    public JsonNode report() {
        return aiClient.owasp();
    }
}
