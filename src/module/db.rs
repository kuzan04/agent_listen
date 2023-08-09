#![allow(dead_code)]
use sqlx::{
    mysql::{MySqlPoolOptions, MySqlPool},
    Row
};
use serde::Serialize;
use oracle::pool::{PoolBuilder, Pool as OraclePool, CloseMode};

// use test
use crate::module::test::*;

#[derive(Debug, Default, Serialize)]
struct Table {
    name: String,
    columns: Vec<String>,
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
                    .map(|row| match row.try_get(format!("Tables_in_{}", self.database.to_lowercase()).as_str()) {
                        Ok(row) => row,
                        Err(_) => row.get(format!("Tables_in_{}", self.database).as_str()),
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
                    mix.push(Table { name: i, columns: res });
                }
                pool.close();
                Ok(serde_json::to_string(&mix).unwrap())
            }
            Err(e) => Ok(e.to_string())
        }
    }

    async fn oracle_query(&self, query: &str, pool: OraclePool) -> Result<Vec<String>, oracle::Error> {
        let conn = pool.get()?;
        match conn.query(query, &[]) {
            Ok(query) => {
                let res = query.into_iter()
                    .map(|row| match row.expect("REASON").get(0) {
                        Ok(row) => row,
                        Err(e) => e.to_string(),
                    })
                    .collect::<Vec<String>>();
                conn.close()?;
                Ok(res)
            }
            Err(err) => Ok(vec![err.to_string()])
        }
    }

    #[allow(unused_must_use)]
    pub async fn oracle(&self) -> Result<String, oracle::Error> {
        //Set Oracle instant client.
        // std::env::set_var("LD_LIBRARY_PATH", "/Users/kuzan04/Desktop/instantclient_19_8/");
        let pool = PoolBuilder::new(self.user.as_str(), self.passwd.as_str(), format!("//{}:1521/{}", self.host, self.database).as_str())
            .max_connections(10)
            .build();
        
        match pool {
            Ok(pool) => {
                let mut mix: Vec<Table> = vec![];
                let tables = self.oracle_query("SELECT table_name FROM user_tables", pool.clone()).await?;
                for i in tables {
                    // let column = self.oracle_query(format!("SELECT column_name FROM all_tab_columns WHERE table_name = '{}' GROUP BY column_name, column_id ORDER BY column_id", i).as_str(), pool.clone()).await?;
                    // function on test only!!
                    let format_cols = format!("SELECT column_name FROM all_tab_columns WHERE table_name = '{}' GROUP BY column_name, column_id ORDER BY column_id", i);
                    let format_name = format!("oracle_query#{}", i);
                    let format_name_static: &'static str = Box::leak(format_name.into_boxed_str());
                    let column = time_function(|| self.oracle_query(&format_cols, pool.clone()), format_name_static).await?;
                    mix.push(Table{ name: i, columns: column});
                }
                // Not sure, ## Can Force to disconnect. ##
                pool.close(&CloseMode::Default);
                Ok(serde_json::to_string(&mix).unwrap())
            }
            Err(e) => Ok(e.to_string())
        }
    }
}

#[derive(Debug)]
pub struct DatabaseCheck {
    connection: MySqlPool,
    from: String,
    table: String,
    columns: Vec<String>,
    content: Vec<String>
}

impl DatabaseCheck {
    pub fn new(connection: MySqlPool, from: String, table: String, columns: Vec<String>, content: Vec<String>) -> Self {
        Self { connection, from, table, columns, content }
    }
}
