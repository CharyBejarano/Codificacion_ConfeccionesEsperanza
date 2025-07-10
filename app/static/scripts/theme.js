

document.addEventListener("DOMContentLoaded", () => {
    const themeSelector = document.getElementById("selector-tema");

    
    const savedTheme = localStorage.getItem("theme") || "default";
    document.body.className = ""; 
    if (savedTheme === "dark") {
        document.body.classList.add("dark-theme");
    }

    
    if (themeSelector) {
        themeSelector.value = savedTheme;

        
        themeSelector.addEventListener("change", (event) => {
            const theme = event.target.value;
            document.body.className = ""; 
            if (theme === "dark") {
                document.body.classList.add("dark-theme");
            }
            localStorage.setItem("theme", theme); 
        });
    }
});