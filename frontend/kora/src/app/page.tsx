export default function Home() {
  return (
    <main className="landing-container">
      <div className="content-wrapper">
        {/* Background SVG */}
        <svg
          className="background-svg"
          width="1665"
          height="1157"
          viewBox="0 0 1665 1157"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g style={{mixBlendMode: 'soft-light'}}>
            <path
              d="M1665 5H1051.55C998.051 5 936.556 25.1669 936.556 94.2494C936.556 140.247 936.557 260.162 936.557 346.122C936.557 385.168 928.545 406.682 903.059 429.793C877.573 452.904 855.563 456.396 798.567 456.396H139.118C80.1227 456.396 38.6259 480.425 19.1274 516.039C2.68294 546.075 5.12852 616.444 5.12853 671.796L5.1285 800.95C5.1285 846.862 20.1274 877.756 50.125 896.207C80.2264 914.721 118.62 921.952 173.616 921.952H1074.55C1107.54 921.952 1152.54 926.535 1193.54 900.498C1227.03 879.224 1233.03 841.284 1233.03 812.107V519.863C1233.03 486.394 1236.98 464.966 1256.53 454.642C1276.03 444.344 1289.53 444.773 1312.03 444.773H1526.01C1540.51 444.773 1553.01 444.773 1564.01 455.5C1573.51 464.764 1573.51 472.234 1573.51 485.107V1071C1574.01 1082.3 1576.01 1113.91 1592.51 1129.78C1614.8 1151.24 1636.5 1151.24 1665 1151.24"
              stroke="white"
              strokeWidth="10"
              strokeDasharray="20 40 60 80"
            />
          </g>
        </svg>

        {/* Main heading */}
        <h1 className="main-heading">kora.</h1>

        {/* Sea turtle image */}
        <img
          src="https://api.builder.io/api/v1/image/assets/TEMP/472fe668b4a15471bbc91dff1f1f01a2bb09d7bb?width=358"
          alt="sea turtle"
          className="turtle-image"
        />

        {/* Subtitle */}
        <h2 className="subtitle">
          Plan your next adventure, <span className="emphasis">sustainably</span>
        </h2>

        {/* Carbon calculator card */}
        <div className="carbon-card">
          <div className="carbon-text">
            <span className="text-secondary">Every journey leaves a </span>
            <span className="footprint-text">footprint</span>
            <span className="text-primary">. </span>
            <br />
            <span className="text-secondary">With our </span>
            <span className="carbon-calculator-text">carbon calculator</span>
            <span className="text-secondary">, you can see the environmental impact of your travel plans!</span>
            <br />
            <br />
            <span className="text-secondary">Make </span>
            <span className="climate-conscious-text">climate-conscious decisions</span>
            <span className="text-secondary"> without compromising your experience.</span>
          </div>

          {/* Action buttons */}
          <div className="button-container">
            <button className="create-profile-btn">
              Create Your Profile
            </button>
            <button className="login-btn">
              Login
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
