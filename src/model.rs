use serde::{Deserialize, Serialize};
use sqlx::{FromRow, mysql::MySqlRow, Row};

#[derive(Debug, Deserialize, Serialize)]
#[allow(non_snake_case)]
pub struct AgentStore {
  name: String,
  pub code: String,
  _type_: String,
  _limit_: i32,
  pub status: i32,
  hide: i32,
}
impl FromRow<'_, MySqlRow> for AgentStore {
  fn from_row(row: &MySqlRow) -> Result<Self, sqlx::Error> {
    let name: String = row.try_get("name")?;
    let code: String = row.try_get("code")?;
    let _type_: String = row.try_get("type")?;
    let _limit_: i32 = row.try_get("_limit_")?;
    let status: i32 = row.try_get("status")?;
    let hide: i32 = row.try_get("hide")?;

    Ok(Self { name, code, _type_, _limit_, status, hide})
  }
}

#[derive(Debug, Deserialize, Serialize)]
#[allow(non_snake_case)]
pub struct AgentManage {
  agm_id: i32,
  agm_name: String,
  ags_id: i32,
  config_detail: String,
  agm_token: String,
}
impl FromRow<'_, MySqlRow> for AgentManage {
  fn from_row(row: &MySqlRow) -> Result<Self, sqlx::Error> {
    let agm_id: i32 = row.try_get("agm_id")?;
    let agm_name: String = row.try_get("agm_name")?;
    let ags_id: i32 = row.try_get("ags_id")?;
    let config_detail: String = row.try_get("config_detail")?;
    let agm_token: String = row.try_get("agm_token")?;

    Ok(Self{ agm_id, agm_name, ags_id, config_detail, agm_token})
  }
}

#[derive(Debug, Deserialize, Serialize)]
#[allow(non_snake_case)]
pub struct AgentHistory {
  agm_id: i32,
}
impl FromRow<'_, MySqlRow> for AgentHistory {
  fn from_row(row: &MySqlRow) -> Result<Self, sqlx::Error> {
    let agm_id: i32 = row.try_get("agm_id")?;
    Ok(Self{ agm_id })
  }
}
