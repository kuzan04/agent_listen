extern crate dotenv;

use dotenv::dotenv;
use get_if_addrs::get_if_addrs;
use sqlx::mysql::MySqlPoolOptions;
use std::fs;
use std::thread;
use std::time::Duration;

mod module;
mod model;
use crate::module::listen::Recevie;

fn set_init() -> String {
    match fs::metadata(".env").is_ok() {
        true => "Success".to_string(),
        false => {
            println!("[Error] Please check file .env");
            std::process::exit(1);
        }
    }
}

fn get_ip(name: String) -> String {
    let mut ip = String::new();
    if let Ok(interfaces) = get_if_addrs() {
        for interface in interfaces {
            if !interface.is_loopback() && interface.name == name && interface.ip().is_ipv4() {
                ip =  interface.ip().to_string();
                break
            } else {
                ip = "None".to_string();
            }
        } 
    } else {
        ip = "Failed".to_string();
    }
    ip
}

#[allow(unused_must_use)]
#[tokio::main]
async fn main() {
    // Get varriable from file .env.
    dotenv().ok();
    // Check file .env
    set_init();
    // Check and create tls to use socket.
    let ip: String;
    loop {
        let i = get_ip(dotenv::var("INTERFACE").unwrap_or_else(|_| "ens192".to_string()));
        match i.to_owned().as_str() {
            "None" => {
                println!("[Warning] Unknow ip from interfaces wait for 15 seconds script rebooting.");
                thread::sleep(Duration::from_secs(15));
            },
            "Failed" => {
                println!("Failed to retrieve interface addresses");
            },
            _ => {
                break ip = i
            },
        }
    }
    // Main database to use.
    let database_url = format!("mysql://{}:{}@{}:{}/{}",
        dotenv::var("DB_USER").unwrap_or_else(|_| "root".to_string()),
        dotenv::var("DB_PASSWORD").unwrap_or_else(|_| "root".to_string()),
        dotenv::var("DB_HOST").unwrap_or_else(|_| "Passw0rd".to_string()),
        dotenv::var("DB_DB_PORT").unwrap_or_else(|_| "3306".to_string()),
        dotenv::var("DB_NAME").unwrap_or_else(|_| "DOL_PDPA".to_string()),
    );
    // Create connect pool.
    let pool = match MySqlPoolOptions::new()
        .max_connections(10)
        .connect(&database_url)
        .await {
            Ok(pool) => {
                pool
            }
            Err(e) => {
                println!("Failed to connect the database: {:?}", e);
                std::process::exit(1);
            }
        };
    // Start listener socket.
    Recevie::new(ip, dotenv::var("PORT").unwrap_or_else(|_| 5050.to_string())).listen(pool).await;
}
