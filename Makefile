# 서버 실행
run:
	python3 main.py

########################
##### Git #####
########################
git-ignore-apply:
	git rm -r --cached .
	git add .
	git commit -m "chore: Apply .gitignore"
	git push origin develop