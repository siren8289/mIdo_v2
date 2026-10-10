package com.mido;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * MIDO 백엔드 시작점.
 *
 * [요청 흐름]
 * React(front) → Spring(back, 이 서버) → FastAPI(ai)
 *                      ↓
 *                 DB(분석 기록 저장)
 */
@SpringBootApplication
public class MidoApplication {

    public static void main(String[] args) {
        SpringApplication.run(MidoApplication.class, args);
    }
}
