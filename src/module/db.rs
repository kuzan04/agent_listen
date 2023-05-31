#![allow(dead_code)]
use sqlx::{mysql::MySqlPoolOptions, Row};
use serde::Serialize;
use oracle::pool::PoolBuilder;

// use crate::model::FilterMySqlTable;
//
#[derive(Debug, Default, Serialize)]
struct Table {
    name: String,
    column: Vec<String>,
}

#[derive(Debug)]
pub struct TestConnect {
    host: String,
    user: String,
    passwd: String,
    database: String,
}
impl TestConnect {
    pub fn new(host: String, user: String, passwd: String, database: String) -> TestConnect {
        TestConnect { host, user, passwd, database }
    }

    #[allow(unused_must_use)]
    pub async fn mysql(&self) -> Result<String, sqlx::Error> {
        let database_url = format!("mysq://{}:{}@{}:3306/{}", self.user, self.passwd, self.host, self.database);
        let pool = MySqlPoolOptions::new()
            .max_connections(10)
            .connect(&database_url)
            .await;
        match pool {
            Ok(pool) => {
                let tables: Vec<String> = sqlx::query("SHOW TABLES")
                    .fetch_all(&pool)
                    .await.unwrap()
                    .into_iter()
                    .map(|row| match row.try_get(format!("Tables_in_{}", self.database).as_str()) {
                        Ok(row) => row,
                        Err(_) => row.get(format!("Tables_in_{}", self.database.to_lowercase()).as_str()),
                    })
                    .collect();
                let mut mix: Vec<Table> = vec![];
                for i in tables {
                    let res: Vec<String> = sqlx::query(&format!("DESCRIBE {}", i))
                        .fetch_all(&pool)
                        .await.unwrap()
                        .into_iter()
                        .map(|row| row.get("Field"))
                        .collect();
                    mix.push(Table { name: i, column: res });
                }
                pool.close();
                Ok(serde_json::to_string(&mix).unwrap())
            }
            Err(e) => Ok(e.to_string())
        }
    }

    pub async fn oracle(&self) -> Result<String, oracle::Error> {
        //Set Oracle instant client.
        // std::env::set_var("LD_LIBRARY_PATH", "/Users/kuzan04/Desktop/instantclient_19_8/");
        let pool = PoolBuilder::new(self.user.as_str(), self.passwd.as_str(), format!("//{}:1521/{}", self.host, self.database).as_str())
            .max_connections(5)
            .build();
        match pool {
            Ok(conn) => {
                match conn.get() {
                    Ok(conn) => {
                        println!("{:?}", conn);
                        Ok("Hello".to_string())
                    },
                    Err(e) => Ok(e.to_string())
                }
            },
            Err(e) => Ok(e.to_string())
        }
    }
}
