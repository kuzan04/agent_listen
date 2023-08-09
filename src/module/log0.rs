use sqlx::mysql::MySqlPool;

// use test!!
use crate::module::test::*;

#[derive(Debug)]
pub struct LogHash {
    connection: MySqlPool,
    table: String,
    column: Vec<String>, 
    content: Vec<String>,
}
impl LogHash {
    pub fn new(connection: MySqlPool, table: String, column: Vec<String>, content: Vec<String>) -> LogHash {
        LogHash { connection, table, column, content }
    }

    // Helper client rerun.
    async fn check(&mut self) -> bool {
        let value_where = self.content
            .iter()
            .zip(self.column.iter())
            .map(|(x, y)| format!("{}=\"{}\"", y.trim(), x.trim()))
            .collect::<Vec<String>>();
        let mut query2 = String::new();
        for i in 0..value_where.len() {
            if i == value_where.len() - 1 {
                query2.push_str(&value_where[i]);
            } else {
                query2.push_str(format!("{} AND ", value_where[i]).as_str());
            }
        }
        let query = "SELECT id FROM (SELECT * FROM TB_TR_PDPA_AGENT_LOG0_HASH ORDER BY id DESC) as log0";
        sqlx::query(format!("{} WHERE {} LIMIT 1", query, query2).as_str())
            .fetch_one(&self.connection)
            .await.is_ok()
    }

    pub async fn build(&mut self) -> Result<String, Box<dyn std::error::Error>> {
        let name = self.content.remove(0);
        match time_function(|| self.check(), "log0_check").await {
            true => Ok(name),
            false => {
                let values = self.content.iter().map(|s| format!("\"{}\"", s)).collect::<Vec<String>>().join(",");
                let query = format!("INSERT INTO {} ({}) VALUES ({})", self.table, self.column.join(","), values);
                sqlx::query(&query)
                    .execute(&self.connection)
                    .await?;
                Ok(name)
            }
        }
    }
}
