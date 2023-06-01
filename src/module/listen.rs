use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net;
use sqlx::{MySqlPool, FromRow};

use crate::module::log0::LogHash;
// use crate::module::file::*;
use crate::module::db::TestConnect;
// use crate::module::sniffer::*;

use crate::model::AgentStore;

#[derive(Debug)]
pub struct Recevie {
    pub host: String,
    pub port: String,
}

impl Recevie {
    pub fn new(host: String, port: String) -> Recevie {
        Recevie { host, port }
    }

    fn split_string(input: &str, delimiter: char) -> Vec<String> {
        input.split(delimiter)
            .map(|s| s.to_string())
            .collect()
    }
    
    async fn test_connect(_type: String, host: String, user: String, passwd: String, database: String) -> String {
        let success: String;
        match _type.parse::<i32>() {
            Ok(t) => { match t {
                    1 => {
                        if let Ok(res) = TestConnect::new(host, user, passwd, database).mysql().await {
                            success = res
                        } else {
                            success = "Query details table error.".to_string()
                        }
                    },
                    0 => {
                        if let Ok(res) = TestConnect::new(host, user, passwd, database).oracle().await {
                            success = res
                        } else {
                            success = "Query details table error.".to_string()
                        }
                    },
                    _ => success = "Hello from Server!".to_string(),
                };
            }
            Err(_) => {
                success = "Failed to read type from client!".to_string()
            }
        };
        success
    }

    fn status_store(query: Vec<AgentStore>, select: String) -> bool {
        let mut result = false;
        let mut i = 0;
        while i != query.len() {
            match &query[i] {
                a if a.code == select => {
                    if a.status == 1 {
                        result = true
                    }
                    i += 1
                },
                _ => i += 1,
            }
        }
        result
    }

    async fn main_task(status: bool, details: Vec<String>, db: MySqlPool) -> String {
        match status {
            true => {
                match details[0].as_str() {
                    "AG1" => {
                        let mut log0_table_all: Vec<String> = dotenv::var("TB_LOG0").unwrap_or_else(|_| "TB_TR_PDPA_AGENT_LOG0_HASH:device_name, os_name, path, name_file, total_line, value, value_md5, value_sha1".to_string())
                            .split(':')
                            .map(|s| s.to_string())
                            .collect();
                        let log0_columns: Vec<String> = log0_table_all.pop().unwrap().split(',').map(|s| s.to_string()).collect();
                        let log0_table = log0_table_all.pop().unwrap();
                        let content = details[details.len() - 1].split("|||").map(|s| s.to_string()).collect::<Vec<String>>();

                        match LogHash::new(db, log0_table, log0_columns, content).build().await {
                            Ok(s) => s,
                            Err(e) => e.to_string(),
                        }
                    },
                    "AG2" => {
                        format!("Hello {}", details[1])
                    },
                    "AG3" => {
                        format!("Hello {}", details[1])
                    },
                    "AG4" => {
                        format!("Hello {}", details[1])
                    }
                    _ => {
                        "Failed".to_string()
                    }
                }
            },
            false => "Close".to_string()
        }
    }

    async fn handle_client(mut stream: net::TcpStream, db: MySqlPool) {
        let mut buffer = [0; 1024];
        match stream.read(&mut buffer).await {
            Ok(bytes_read) => {
                // Main Taskprocess.
                let get_response = String::from_utf8_lossy(&buffer[..bytes_read]);
                // Set message to response to client.
                let message: String;
                match get_response {
                    // Statement test connection sql.
                    s if s.contains('|') && !s.contains('#') => {
                        let conv_test = Self::split_string(&s, '|');
                        // Call check type sql.
                        message = Self::test_connect(conv_test[0].to_owned(), conv_test[1].to_owned(), conv_test[2].to_owned(), conv_test[3].to_owned(), conv_test[4].to_owned()).await;
                        if let Err(error) = stream.write_all(message.as_bytes()).await {
                            println!("Failed to write to stream: {}", error);
                        }
                    },
                    // Statement main task process agent.
                    s if s.contains('#') => {
                        // Get query from agent store to check status.
                        let result_store: Vec<AgentStore> = sqlx::query("SELECT * FROM TB_TR_PDPA_AGENT_STORE")
                            .fetch_all(&db)
                            .await.unwrap()
                            .into_iter()
                            .map(|row| AgentStore::from_row(&row).unwrap())
                            .collect();
                        let conv_response = Self::split_string(&s, '#');
                        message = Self::main_task(Self::status_store(result_store, conv_response[0].to_owned()), conv_response, db).await;
                        if let Err(error) = stream.write_all(message.as_bytes()).await {
                            println!("Failed to write to stream: {}", error);
                        }
                    },
                    _ => {
                        message = "Failed unknow type agent. Please check token, .env, or api from alltra again!!".to_string();
                        if let Err(error) = stream.write_all(message.as_bytes()).await {
                            println!("Failed to write to stream: {}", error);
                        }
                    },
                }
            }
            Err(error) => {
                println!("Failed to read from stream: {}", error);
            }
        }

        stream.shutdown().await.unwrap();
    }

    pub async fn listen(&self, db: MySqlPool) {
        let listener = net::TcpListener::bind(format!("{}:{}", &self.host, &self.port)).await.expect("Failed to bind to address");

        println!("Server listening on {}:{}", &self.host, &self.port);

        loop {
            if let Ok(sock) = listener.accept().await{
                let cloned_db = db.clone();
                tokio::spawn(async move {
                    Self::handle_client(sock.0, cloned_db).await;
                });
            } else {
                eprintln!("Failed accepting connection!");
            }
        }
    }
}
