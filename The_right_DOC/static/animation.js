const observer = new IntersectionObserver((entries) =>{
        entries.forEach((entry) =>{
                console.log(entry)
                if(entry.isIntersecting){
                  entry.target.classList.add('show');
                }else{
                  entry.target.classList.remove('show');
                }
        });
    });

const hidden_el = document.querySelectorAll('.hidden');
hidden_el.forEach((ele) => observer.observe(ele));