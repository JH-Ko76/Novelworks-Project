# novelworks_Project
<p> 
   今回の課題要件は、以下となります。</br>顧客からの問い合わせを AI で自動分類して適切なチーム
   に振り分ける簡易エージェントを AWS上に構築し、ローカルで動くチャット UI から呼び出せるように
   してください。
</p>
<p>
   Gemini AIを使用してバイブコーディングを行いました</br>
   全体の制作時間は、その他の環境設定を含めて約9時間かかりました。
</p>

### コンテンツ
-  [🗺️ 全体システム構成図](#architecture)
-  [✨ 主要機能](#features)
-  [🛠 技術スタック](#tech-stack)
-  [🚀 クイックスタート](#quickstart)
-  [👾 参考 & コード説明](#reference)
   
## 🗺️ 全体システム構成図 <a name="architecture"></a>
<img width="1182" height="630" alt="image" src="https://github.com/user-attachments/assets/a173fa56-e843-495e-b823-0418cde917f6" />


## ✨ 主要機能 <a name="features"></a>
### クリックすると、より大きく表示されます。
機能は以下の通りです。


画面下部の入力欄から問い合わせ内容を入力すると、その内容が自動的に分類され、データベースに保存されるとともに、分類結果が画面に表示されます。



また、問い合わせの分類結果が曖昧で確認が必要な場合には、画像のように修正ボタンを使用して内容を修正し、そのまま保存できる機能を実装しました。


- 分類
<img width="426" height="240" alt="image" src="https://blog.kakaocdn.net/dna/c5NCtE/dJMcacQjBSC/AAAAAAAAAAAAAAAAAAAAAD549wLrkSipnTv53KXoRYd3UFZhIXV54IsF12NtMGra/img.gif?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=sESXI6hxhfvGpECiomSh1ZDmDvg%3D" />

- 確信度が低い場合の修正
<img width="426" height="240" alt="image" src="https://blog.kakaocdn.net/dna/BAqBq/dJMcahKShQZ/AAAAAAAAAAAAAAAAAAAAANqEf6qo3sqiLUodV4rN_iV7ak1Vj4Me8iCHNHy0Qj3j/img.gif?credential=yqXZFxpELC7KVnFOS48ylbz2pIh7yKj8&expires=1777561199&allow_ip=&allow_referer=&signature=j%2FjBOXfDcstIy9%2BvjRYopIhDluo%3D" />


## 🛠 技術スタック<a name="tech-stack"></a>
<h4>🖥 Front End </h4> 
<ol>
  <li> Framework: React 18</li>
  <li> Build Tool: Vite </li>
  <li> Language: TypeScript </li>
  <li> Styling: Tailwind CSS </li>
  <li> HTTP Client: Axios </li>
</ol>
</br>
<h4> Back End (Serverless) </h4> 
<ol>
  <li> Runtime: Python 3.11</li>
  <li> Server : AWS Lambdae </li>
  <li> API Management: Amazon API Gateway </li>
  <li> Database: Amazon DynamoDB </li>
  <li> Security: AWS Secrets Manager </li>
  <li> Monitoring: Amazon CloudWatch </li>
  <li> AI Engine: Google Gemini 2.5 Flash </li>
  <li> Infrastructure as Code : Terraform </li>
</ol>
</br>
<h4>🖥 Tools & Package Management </h4> 
<ol>
  <li> Package Manager: npm </li>
  <li> Runtime Env: Node.js </li>
  <li> SDK: Boto3 </li>
  <li> edit: vscode </li>
</ol>
</br>

## 🚀 クイックスタート<a name="quickstart"></a>
### 1. 要件 
<p>開始する前に、以下の環境が整っている必要があります。</p>

<ol>
   <li><a href="https://nodejs.org/en/blog/release/v24.14.1">Node.js v24.14.1</a></li>
   <li><a href="https://www.python.org/downloads/release/python-3144/">Python v3.14.4</a></li>
  <li><a href="https://releases.hashicorp.com/terraform/1.14.8/">terraform v1.14.8</a></li>
     <li><a href="https://docs.npmjs.com/cli/v11/configuring-npm/install">npm v11.11.0</a></li>
   <li><a href="https://aws.amazon.com/jp/">AWS Account</a></li>
   <li><a href="https://aistudio.google.com/">Gemini API Key</a></li>
   <li><a href="https://code.visualstudio.com/download">Vscode</a></li>
</ol>

### 2. 設置
<p>VScodeのTerminalで次のコマンドを入力してください</p>

### Installation
```bash
#プロジェクトコピー
$git clone https://github.com/JH-Ko76/Novelworks-Project.git
$cd Novelworks-Project
```

### Backend
<p>
   Terraformの設定前に、事前にアクセスキーに関する環境変数の設定が必要です。</br>
   AWSでIAMアカウントを作成し、キーを設定する手順は以下のドキュメントをご確認のうえ、コマンド
   入力する前に事前に実施してください。</br>
   <a
href=https://1drv.ms/b/c/933a10afa28e82e4/IQCfkqRd7WA3QpVwM0eCxSyCAWKOCANon_QLetZSGU4mIfk?e=KCibj7">terraform 設定手順</a>
</p>


```bash
# Winidow パス例: C:\Users\....\Novelworks-Project\back_end
#Novelworks-Project Directoryからback_endに移動します。
$cd ./back_end

#VSCodeのTerminalで以下のコマンドを入力してください
$terraform -v
$terraform init
$terraform plan
$terraform apply

#正常に実行された場合、AWSインフラの作成はこれで完了です。
```
<p>
Google AIを使用するためには、事前にAPIキーの発行が必要です。
発行後は、AWSでキーを管理するための追加設定が必要となるため、
以下のドキュメントにまとめました。
必ず事前に該当手順に従って設定を完了したうえで、プロジェクトを実行してください。</br>
<a href=https://1drv.ms/b/c/933a10afa28e82e4/IQBd7Lvk1vRTRI6x5j3t32wtATyjHJZMIdMambXKvOBMXTs?e=1rkU5s">Google AI API 設定手順</a>
</p>

<p>
   これでバックエンドの設定は完了です。</br>
   インフラを削除する手順は以下の通りです。
</p>


```bash
#Novelworks-Project Directoryからback_endに移動します。
$cd ./back_end
#VSCodeのTerminalで以下のコマンドを入力してください
$terraform destroy
#正常に実行された場合、AWSインフラがすべて削除されます。
```


### FrontEnd

```bash
#nvmをダウンロードしてインストールする
$curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
#シェルを再起動する代わりに実行する
$\. "$HOME/.nvm/nvm.sh"
# Node.jsをダウンロードしてインストールする：
$nvm install 

# Node.jsのバージョンを確認する：
$node -v 
#必要なライブラリをインストールします。 
$npm -v

#TailwindCSSンストール
$npm install -D tailwindcss postcss autoprefixer
$npx tailwindcss init -p

#インストールされたライブラリに既知の脆弱性があるか確認します。
$npm audit

#プロジェクトを実行します。
$npm run dev
```

<p>
   npm の設定が完了したら、API Gateway の設定を行い、npm run dev で再実行できるか確認してください
   <a href=https://1drv.ms/b/c/933a10afa28e82e4/IQA322KDV4zbSIY03uwDAPnVAbFW6iy1mfFAmTOhUQ-PxZI?e=hwkFG3">API Gateway 設定手順</a>

   これでフロントエンドの設定は完了です。</br>
   フロントエンドを削除する手順は以下の通りです。
</p>


```bash
#Window パス例: C:\....\Novelworks-Project\front_end
#削除コマンドを実行すると、該当パス内のすべてのファイルが削除されるため、
#必ず現在のパスを確認してから実行してください。
$Remove-Item -Recurse -Force node_modules, dist, package-lock.json
```


## 👾 参考 & コード説明 <a name="reference"></a>

### Terraform 導入の理由
- 高い可読性と保守性
  <p>
     (1).直感的な状態把握 </br>
     Terraformは宣言型言語であり、インフラの最終状態をコードで明確に記述できるという特徴を持
     っています。そのため、本課題の要件に基づくインフラ構成を直感的に把握するのに適していると判
     断しました。</br>
     
     (2).協業および学習曲線 </br>
     将来的なチームでの協業を考慮した際、コードの可読性が高く、ドキュメントも整備されているた
     め、メンバーの迅速なオンボーディングと円滑なコミュニケーションが可能だと考えました。
  </p>
- 効率的な状態管理
  <p>
     (3).直感的な状態把握 </br>
     terraform.tfstateファイルを通じて、実際にデプロイされたリソースとコード間の状態を同期でき
     るため、変更管理が容易であると考えました。</br>
     
     (4).部分的なアップデートの最適化</br>
     インフラ全体を再デプロイする必要がなく、変更された箇所のみを検知して更新できる特性により、
     今回のようにコードの修正や追加を迅速に行う場面において、開発サイクルの短縮とインフラ運用の
     効率化につながると判断しました。
  </p>
- 開発生産性および完成度の最大化
  <p>    
     (5).時間リソースの戦略的配分</br>
     新しいIaCツールの習得にかかる埋没コストを抑える代わりに、これまでの学習経験を活かして
     Terraformの機能を積極的に活用し、システムの安定性確保に注力しました。
  </p>

### AWS サービス選定理由
- API Gateway
  
     (1).セキュリティ & 可用性 </br>
     作成したLambdaロジックがパブリックインターネットに直接公開されないよう、一次的なエンドポ
     イントとして採用しました。 </br>
     また、秒間リクエスト数を制限する設定により、大量トラフィックなどの異常アクセスを事前に遮断
     できる点にメリットがあるため採用しました。
  
     
     (2).拡張性 </br>
     将来的にサービスを拡張し、複数のLambda関数やサービスが増えた場合でも、クライアント側で追加
     設定を行う必要がなく、API Gatewayという単一のエンドポイントを経由することで複雑さを軽減で
     きると考えました。
  
  
     また、IAMやCognitoなどと連携することで、各関数ごとに個別のセキュリティロジックを実装する
     必要がなく、API Gateway側で一括して認証・認可の検証が可能になる点にも利点があると考えまし
     た。
     
     さらに、CloudWatchを利用することで、エラーログ、呼び出し成功、レスポンスタイムなどの各種ログ
     を統合的に管理できる点にもメリットがあると考えました。

  
- AWS Lambda & DynamoDB
  
  (1). コスト効率性 </br>
  固定的なサーバー維持費がかからず、問い合わせが発生して関数が実行されたときにのみ課金される
  ため、この点がチャットボットのようなシステムに適していると考えました。

  
  (2). セキュリティ </br>
  Lambdaのサーバーレス方式により、サーバーが常時稼働することで発生し得る脆弱性を防止できると考え
  採用しました。
  

  (3). 拡張性 </br>
  ユーザー数が急増した場合でも、別途インフラ設定を行うことなく、AWSが自動的にインスタンスを 
  スケールできる点がサービスの安定性向上につながると考え、採用しました。


-  AWS Secrets Manager

   (1). ハードコーディングの防止 </br>
   Secrets Managerを使用した最も根本的な理由は、APIキーのような機密情報を平文で露出させず、
   別の安全なストレージに保管することで、Gitなどのコード管理ツールを通じた漏洩を防ぐためです。

   
   (2). 認証情報の一元管理 </br>
   キーを変更する必要がある場合でも、コードを修正することなく、すべてのサービスに反映できる
   という管理上の利点があるため採用しました。

   
   (3). アクセス制御と暗号化 </br>
   IAMにより特定のLambda関数のみがキーを読み取れるように詳細なアクセス制御が可能である点と、
   データの保存および転送時にKMSによる暗号化が行われることで安全性を高められると考え、
   採用しました。

   
   (4). キーローテーション </br>
   Secrets Managerの機能の一つとして、今後プロジェクトが拡張された場合、セキュリティポリシーの
  観点からパスワードやAPIキーは長期間使用せず、定期的にローテーションすることが推奨されます。</br>
  Secrets Managerはこのようなキー管理を自動化できるため、その利点を考慮し、将来的な拡張も見据
  えて採用しました。
  
  
-  Amazon CloudWatch 
   
   (1). リアルタイムモニタリングとトラブルシューティング </br>
   システム開発の過程において、サーバーへデータを送信する際に発生したエラー情報や、さまざまな
   エラー内容を確認することで、より迅速に問題を特定し対応することができました。

### Vite + React + TypeScriptを選択した理由
- Vite + React
   
   (1). 高速なフィードバックループ </br>
   今回の課題の中心である「AI分類ロジック」および「AWSインフラ構築」に集中するため、ビルドおよび
   変更反映速度が最も高速なViteを選択しました。リアルタイムで結果を確認しながら開発できるため、
   開発時間を大幅に短縮することができました。

     
   (2). リアルタイムモニタリングとトラブルシューティング </br>
   複雑な設定なしで即座にUIを構築できる点が大きな利点でした。特にCSSを別ファイルで管理するのではなく、
   コンポーネント内で管理する方式を採用し、デザイン実装の工数を削減することで、API連携やビジネスロジック
   などのコア部分により集中できるようにしました。

- TypeScript
     
   (1). 自主的な学習 </br>
   以前から興味のあったTypeScriptを実際のプロジェクトに適用し、開発過程で自らコードレビューを行いながら
   学習を進める目的で採用しました。

### 実際にサービスとして運用する場合必要だと思う点

- シークレットマネージャーによるキー管理の改善 </br>
   サービスを拡張する場合、現在は秘密情報を平文で管理しているため、セキュリティと管理性の観点から、
   JSON形式で構造化し、AWS Secrets Managerなどを活用した管理方法へ改善する必要があると考えました。


- 概算コストの算出と可用性の改善 </br>
   実際にサービスとして運用する場合、Lambdaはリクエスト数に応じた従量課金であり、
   月100万リクエストまでは無料枠があるため、ユーザー数の増加に応じてスケーリング可能だと考えています。
   一方でAPI GatewayやSecrets Managerなどは利用量や管理対象の増加に伴いコストが発生するため、
   サービス拡張を前提とした具体的なコスト試算が必要だと考えました。


- API Gatewayへの認証機構の導入 </br>
   現状では誰でもAPIへアクセス可能な状態となっているため、リソースの不正利用や過負荷のリスクがあります。
   そのため、本番環境では認証・認可を導入し、許可されたユーザーまたは正規のフロントエンドのみがアクセス
   できる仕組みが必要だと考えました


- 今後のサービス拡張について </br>
   Few-shotの例示データだけでなく、ユーザーの問い合わせデータをデータベースに蓄積し、
   それを学習データとして活用することで、より実際の利用シーンに特化したAI精度の向上が
   可能になると考えています。


- AI APIの利用制限について </br>
    実際にAI APIを利用してみたところ、テスト段階でも無料枠の消費が想定より早く進む印象がありました。
    そのため本番環境での運用を前提とする場合は、有料プランへの移行やコスト管理の設計が必要だと認識
    しました。


- セキュリティ対策の強化について </br>
    短期間での開発ということもあり、フロントエンドの脆弱性やプロンプトインジェクションなどAI特有の攻撃に
    対する検証が十分ではありませんでした。
    そのため、本番環境ではこれらのリスクに対するセキュリティ対策の検証と強化が必要だと考えています
   

### AI 活用・突破力レポートは以下をご参照ください。
<a href="https://1drv.ms/b/c/933a10afa28e82e4/IQCPtQN7FU5wSoMyUQQMnxLKAWv7wdKzxMT3JTUIbZttLKg?e=vA5AUU"> AI 活用・突破力レポート</a>

