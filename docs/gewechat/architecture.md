flowchart TB
  subgraph "Frontend"
    FC[GewechatLogin Component]
    FUI[User Interface]
  end

  subgraph "Backend API"
    AP[API Routes]
    AC[Gewechat Client]
  end

  subgraph "Gewechat Service"
    GS[Gewechat Server]
    DB[(Database)]
    QR[QR Code Generator]
    WXP[WeChat Protocol]
  end

  subgraph "Config Storage"
    CF[Config Files]
  end

  User[User] -- Scans QR Code --> FUI
  FC -- Displays --> FUI
  FC -- API Requests --> AP
  AP -- Calls --> AC
  AC -- HTTP Request --> GS
  GS -- Generates --> QR
  QR -- Returns --> AC
  GS -- Stores Data --> DB
  GS -- Communicates --> WXP
  WXP -- WeChat Network --> Cloud[(WeChat Cloud)]
  AP -- Saves Config --> CF
  
  classDef frontendClass fill:#d9f7be,stroke:#91d5ff,stroke-width:2px;
  classDef backendClass fill:#91caff,stroke:#096dd9,stroke-width:2px;
  classDef serviceClass fill:#ffd8bf,stroke:#fa8c16,stroke-width:2px;
  classDef storageClass fill:#d3adf7,stroke:#722ed1,stroke-width:2px;
  classDef userClass fill:#fff,stroke:#d9d9d9,stroke-width:2px;
  classDef cloudClass fill:#f0f0f0,stroke:#8c8c8c,stroke-width:2px;
  
  class FC,FUI frontendClass;
  class AP,AC backendClass;
  class GS,DB,QR,WXP serviceClass;
  class CF storageClass;
  class User userClass;
  class Cloud cloudClass;
