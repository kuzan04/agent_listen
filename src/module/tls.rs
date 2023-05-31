#![allow(dead_code)]
use rcgen::{Certificate, CertificateParams, DnType, DistinguishedName, RcgenError};
use std::path::Path;
use std::fs::{File, create_dir};
use std::io::Write;

#[derive(Debug)]
pub struct Ssl {
    pub country_name: String,
    pub state_province: String,
    pub organization_name: String,
    pub common_name: String,
}
impl Ssl {
    pub fn handle_generate_tls(&self) -> Result<(), RcgenError> {
        let mut params = CertificateParams::default();
        params.alg = &rcgen::PKCS_ECDSA_P256_SHA256;
        params.distinguished_name = DistinguishedName::new();
        params.distinguished_name.push(DnType::CountryName, &self.country_name);
        params.distinguished_name.push(DnType::StateOrProvinceName, &self.state_province);
        params.distinguished_name.push(DnType::OrganizationName, &self.organization_name);
        params.distinguished_name.push(DnType::CommonName, &self.common_name);
        let cert = Certificate::from_params(params)?;

        let path = Path::new("ssl");
        if !path.exists() {
            create_dir(path).expect("Failed to create directory");
        }

        let cert_pem = cert.serialize_pem();
        let mut cert_file = File::create("ssl/agent.crt").expect("Filed can't create");
        cert_file.write_all(cert_pem?.as_bytes()).expect("Filed to write .crt");

        let private_key_pem = cert.serialize_private_key_pem();
        let mut private_key_file = File::create("ssl/agent.key").expect("Filed can't create");
        private_key_file.write_all(private_key_pem.as_bytes()).expect("Filed to write .key");

        Ok(())
    }
}
