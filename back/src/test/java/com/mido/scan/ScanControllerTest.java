package com.mido.scan;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mido.ai.AiClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** AI 서버는 가짜(Mock)로 바꾸고, Spring의 저장·조회 흐름만 확인한다. */
@SpringBootTest
@AutoConfigureMockMvc
class ScanControllerTest {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    ObjectMapper objectMapper;

    @MockBean
    AiClient aiClient;

    @Test
    void createAndGet() throws Exception {
        given(aiClient.analyze(any())).willReturn(objectMapper.readTree("""
                {"file_type":"package.json",
                 "summary":{"dependency_count":1,"vulnerability_count":2,"kev_count":1,"level":"critical"},
                 "explanation":"lodash를 먼저 고치세요.","explanation_source":"basic",
                 "findings":[]}
                """));

        mockMvc.perform(post("/api/scans")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"manifest\":\"{\\\"dependencies\\\":{\\\"lodash\\\":\\\"4.17.15\\\"}}\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.level").value("critical"))
                .andExpect(jsonPath("$.kevCount").value(1));

        mockMvc.perform(get("/api/scans"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].fileType").value("package.json"));
    }

    @Test
    void emptyManifestReturns400() throws Exception {
        mockMvc.perform(post("/api/scans")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"manifest\":\"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errorCode").value("VALIDATION_ERROR"));
    }
}
