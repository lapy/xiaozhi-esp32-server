package xiaozhi.modules.knowledge.rag;

import java.time.Duration;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Map;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

import java.text.SimpleDateFormat;
import java.util.TimeZone;
import java.util.Locale;
import java.net.URLEncoder;
import java.io.UnsupportedEncodingException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.URI;
import java.io.OutputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.function.Consumer;

import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.extern.slf4j.Slf4j;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;

/**
 * RAGFlow HTTP Client
 * Handles HTTP communication, authentication, timeouts, and error parsing.
 */
@Slf4j
public class RAGFlowClient {

    private final String baseUrl;
    private final String apiKey;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    // Default timeout in seconds.
    private static final int DEFAULT_TIMEOUT = 30;

    public RAGFlowClient(String baseUrl, String apiKey) {
        this(baseUrl, apiKey, DEFAULT_TIMEOUT);
    }

    public RAGFlowClient(String baseUrl, String apiKey, int timeoutSeconds) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.apiKey = apiKey;
        this.objectMapper = new ObjectMapper();
        // Support RFC 1123 dates returned by RAGFlow, such as Tue, 10 Feb 2026 10:27:35 GMT.
        this.objectMapper
                .setDateFormat(new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss 'GMT'", Locale.US));
        this.objectMapper.setTimeZone(TimeZone.getTimeZone("GMT"));

        // Prefer a pooled RestTemplate bean from the Spring context when available.
        RestTemplate pooledTemplate = null;
        try {
            pooledTemplate = xiaozhi.common.utils.SpringContextUtils.getBean(RestTemplate.class);
        } catch (Exception e) {
            log.warn("Unable to load pooled RestTemplate from SpringContext, falling back to simple connection mode: {}",
                    e.getMessage());
        }

        if (false) { // Force new RestTemplate for debugging
            this.restTemplate = pooledTemplate;
            log.debug("RAGFlowClient attached the global pooled RestTemplate successfully");
        } else {
            // Fallback path: configure timeouts and create a simple RestTemplate.
            log.info("RAGFlowClient initialized with an independent RestTemplate (debug mode)");
            SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
            factory.setConnectTimeout(timeoutSeconds * 1000);
            factory.setReadTimeout(timeoutSeconds * 1000);
            this.restTemplate = new RestTemplate(factory);
        }
    }

    /**
     * Send a GET request.
     */
    public Map<String, Object> get(String endpoint, Map<String, Object> queryParams) {
        String url = buildUrl(endpoint, queryParams);
        log.debug("GET {}", url);
        return execute(url, HttpMethod.GET, null);
    }

    /**
     * Send a POST request with JSON.
     */
    public Map<String, Object> post(String endpoint, Object body) {
        String url = buildUrl(endpoint, null);
        log.info("RAGFlow Client POST Request: URL={}, BodyType={}", url,
                body != null ? body.getClass().getName() : "null");
        try {
            return execute(url, HttpMethod.POST, body);
        } catch (Exception e) {
            log.error("RAGFlow Client POST Failed: URL={}", url, e);
            throw e;
        }
    }

    /**
     * Send a DELETE request.
     */
    public Map<String, Object> delete(String endpoint, Object body) {
        String url = buildUrl(endpoint, null);
        log.debug("DELETE {}", url);
        return execute(url, HttpMethod.DELETE, body);
    }

    /**
     * Send a PUT request.
     */
    public Map<String, Object> put(String endpoint, Object body) {
        String url = buildUrl(endpoint, null);
        log.debug("PUT {}", url);
        return execute(url, HttpMethod.PUT, body);
    }

    /**
     * Send a multipart request for file upload.
     */
    public Map<String, Object> postMultipart(String endpoint, MultiValueMap<String, Object> parts) {
        String url = buildUrl(endpoint, null);
        log.debug("POST MULTIPART {}", url);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        headers.setBearerAuth(apiKey);
        // Some environments may require charset handling for non-ASCII file names, but multipart usually relies on part headers.

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(parts, headers);

        return doExecute(url, HttpMethod.POST, requestEntity);
    }

    private Map<String, Object> execute(String url, HttpMethod method, Object body) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(apiKey);
        // Force UTF-8.
        headers.setAcceptCharset(Collections.singletonList(StandardCharsets.UTF_8));

        HttpEntity<Object> requestEntity = new HttpEntity<>(body, headers);
        return doExecute(url, method, requestEntity);
    }

    private Map<String, Object> doExecute(String url, HttpMethod method, HttpEntity<?> requestEntity) {
        try {
            ResponseEntity<String> response = restTemplate.exchange(url, method, requestEntity, String.class);

            if (!response.getStatusCode().is2xxSuccessful()) {
                log.error("RAGFlow API Error Status: {}", response.getStatusCode());
                throw new RenException(ErrorCode.RAG_API_ERROR, "HTTP " + response.getStatusCode());
            }

            String responseBody = response.getBody();
            if (responseBody == null) {
                throw new RenException(ErrorCode.RAG_API_ERROR, "Empty Response");
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> map = objectMapper.readValue(responseBody, Map.class);

            Integer code = (Integer) map.get("code");
            if (code != null && code != 0) {
                String msg = (String) map.get("message");
                log.error("RAGFlow Business Error: code={}, msg={}", code, msg);
                throw new RenException(ErrorCode.RAG_API_ERROR, msg != null ? msg : "Unknown RAGFlow Error");
            }

            // Return the full response map after validating code != 0 here.
            // This keeps the client flexible while centralizing business-error handling.
            return map;

        } catch (RenException re) {
            throw re;
        } catch (Exception e) {
            log.error("RAGFlow Client Execute Error! URL: {}, Method: {}, Body Type: {}", url, method,
                    requestEntity.getBody() != null ? requestEntity.getBody().getClass().getName() : "null");
            log.error("Full exception stack trace: ", e);
            throw new RenException(ErrorCode.RAG_API_ERROR, "Request Failed: " + e.getMessage());
        }
    }

    private String buildUrl(String endpoint, Map<String, Object> queryParams) {
        StringBuilder sb = new StringBuilder(baseUrl);
        if (!endpoint.startsWith("/")) {
            sb.append("/");
        }
        sb.append(endpoint);

        if (queryParams != null && !queryParams.isEmpty()) {
            sb.append("?");
            queryParams.forEach((k, v) -> {
                if (v != null) {
                    try {
                        sb.append(k).append("=")
                                .append(URLEncoder.encode(v.toString(),
                                        StandardCharsets.UTF_8.name()))
                                .append("&");
                    } catch (UnsupportedEncodingException e) {
                        log.warn("Failed to encode query parameter: k={}, v={}", k, v);
                        sb.append(k).append("=").append(v).append("&");
                    }
                }
            });
            // Remove the trailing ampersand.
            sb.setLength(sb.length() - 1);
        }
        return sb.toString();
    }

    /**
     * Send a streaming POST request using SSE.
     * Implemented with the Java 21 HttpClient.
     *
     * @param endpoint API endpoint
     * @param body     request body
     * @param onData   callback invoked for each received line
     */
    public void postStream(String endpoint, Object body, Consumer<String> onData) {
        try {
            String url = buildUrl(endpoint, null);
            log.debug("POST STREAM {}", url);

            String jsonBody = objectMapper.writeValueAsString(body);

            HttpClient httpClient = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(DEFAULT_TIMEOUT))
                    .build();

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .header("Content-Type", "application/json")
                    .header("Authorization", "Bearer " + apiKey)
                    .POST(HttpRequest.BodyPublishers.ofString(jsonBody, StandardCharsets.UTF_8))
                    .build();

            // Send the request and process the streaming response.
            httpClient.send(request, HttpResponse.BodyHandlers.ofInputStream())
                    .body()
                    .transferTo(new OutputStream() {
                        private final ByteArrayOutputStream buffer = new ByteArrayOutputStream();

                        @Override
                        public void write(int b) throws IOException {
                            if (b == '\n') {
                                String line = buffer.toString(StandardCharsets.UTF_8);
                                if (!line.trim().isEmpty()) {
                                    onData.accept(line);
                                }
                                buffer.reset();
                            } else {
                                buffer.write(b);
                            }
                        }
                    });

        } catch (Exception e) {
            log.error("RAGFlow Stream Request Error", e);
            throw new RenException(ErrorCode.RAG_API_ERROR, "Stream Request Failed: " + e.getMessage());
        }
    }
}
