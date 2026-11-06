//! RedLamp Backend Proxy & Computation Service in Rust
//! Nhận CSV và tên model, chuyển tiếp hoặc thực thi inference và trả về kết quả JSON:
//! { input, pred, pred_label, pred_enc, mse_raw, ce_raw, threshold, flagged_regions, conclusion }

use actix_cors::Cors;
use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
struct AnalyzePayload {
    model_id: String,
    csv_text: Option<String>,
    sample_name: Option<String>,
    n_train: Option<usize>,
    threshold_val: Option<f64>,
}

#[derive(Debug, Serialize)]
struct HealthResponse {
    status: &'static str,
    service: &'static str,
    python_engine_url: &'static str,
}

#[get("/api/health")]
async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(HealthResponse {
        status: "healthy",
        service: "RedLamp Rust Backend Gateway",
        python_engine_url: "http://127.0.0.1:8000",
    })
}

#[post("/api/rust/analyze")]
async fn proxy_analyze(
    payload: web::Json<AnalyzePayload>,
    client: web::Data<reqwest::Client>,
) -> impl Responder {
    // Chuyển tiếp tới Python PyTorch inference server và nhận kết quả JSON
    let python_url = "http://127.0.0.1:8000/api/analyze";
    match client.post(python_url).json(&payload.into_inner()).send().await {
        Ok(res) => {
            let status = res.status();
            match res.bytes().await {
                Ok(bytes) => HttpResponse::build(status)
                    .content_type("application/json")
                    .body(bytes),
                Err(e) => HttpResponse::InternalServerError().body(format!("Failed reading response: {}", e)),
            }
        }
        Err(e) => HttpResponse::BadGateway().body(format!("Failed reaching Python engine: {}", e)),
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    let client = reqwest::Client::new();
    println!("RedLamp Rust Service running on http://127.0.0.1:8080");

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(client.clone()))
            .wrap(Cors::permissive())
            .service(health_check)
            .service(proxy_analyze)
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}

